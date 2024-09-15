from neo4j import GraphDatabase
import hashlib
from embed import EmbeddingModel


class InsertDoc():
    
    def __init__(self, neo4j_url, neo4j_user, neo4j_password, neo4j_database="neo4j", google_api_key=None):
        self.neo4j_url = neo4j_url
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.neo4j_database = neo4j_database
        self.google_api_key = google_api_key
        self.initialise_neo4j()
        self.embed_model = self.load_embedding_model(google_api_key)
        
    def load_embedding_model(self, google_api_key):
        return EmbeddingModel(google_api_key)

    def initialise_neo4j(self):
        cypher_schema = [
            "CREATE CONSTRAINT sectionKey IF NOT EXISTS FOR (c:Section) REQUIRE (c.key) IS UNIQUE;",
            "CREATE CONSTRAINT chunkKey IF NOT EXISTS FOR (c:Chunk) REQUIRE (c.key) IS UNIQUE;",
            "CREATE CONSTRAINT documentKey IF NOT EXISTS FOR (c:Document) REQUIRE (c.url_hash) IS UNIQUE;",
            #"CALL db.index.vector.createNodeIndex('chunkVectorIndex', 'Embedding', 'value', 768, 'COSINE');"
        ]

        driver = GraphDatabase.driver(self.neo4j_url, database=self.neo4j_database, auth=(self.neo4j_user, self.neo4j_password))

        with driver.session() as session:
            
            
            # Check if the vector index exists before creating it
            check_index_query = "SHOW INDEXES WHERE name = 'chunkVectorIndex'"
            result = session.run(check_index_query)
                
            for cypher in cypher_schema:
                session.run(cypher)
            if not result.single():
                create_index_query = "CALL db.index.vector.createNodeIndex('chunkVectorIndex', 'Embedding', 'value', 768, 'COSINE');"
                session.run(create_index_query)
        driver.close()

        
        
    def ingestDocumentNeo4j(self, doc, doc_location):

        cypher_pool = [
            # 0 - Document
            "MERGE (d:Document {url_hash: $doc_url_hash_val}) ON CREATE SET d.url = $doc_url_val RETURN d;",  
            # 1 - Section
            "MERGE (p:Section {key: $doc_url_hash_val+'|'+$block_idx_val+'|'+$title_hash_val}) ON CREATE SET p.page_idx = $page_idx_val, p.title_hash = $title_hash_val, p.block_idx = $block_idx_val, p.title = $title_val, p.tag = $tag_val, p.level = $level_val RETURN p;",
            # 2 - Link Section with the Document
            "MATCH (d:Document {url_hash: $doc_url_hash_val}) MATCH (s:Section {key: $doc_url_hash_val+'|'+$block_idx_val+'|'+$title_hash_val}) MERGE (d)<-[:HAS_DOCUMENT]-(s);",
            # 3 - Link Section with a parent section
            "MATCH (s1:Section {key: $doc_url_hash_val+'|'+$parent_block_idx_val+'|'+$parent_title_hash_val}) MATCH (s2:Section {key: $doc_url_hash_val+'|'+$block_idx_val+'|'+$title_hash_val}) MERGE (s1)<-[:UNDER_SECTION]-(s2);",
            # 4 - Chunk
            "MERGE (c:Chunk {key: $doc_url_hash_val+'|'+$block_idx_val+'|'+$sentences_hash_val}) ON CREATE SET c.text = $sentences_val, c.sentences_hash = $sentences_hash_val, c.block_idx = $block_idx_val, c.page_idx = $page_idx_val, c.tag = $tag_val, c.level = $level_val, c.embedding = $embedding_val RETURN c;",
            # 5 - Link Chunk to Section
            "MATCH (c:Chunk {key: $doc_url_hash_val+'|'+$block_idx_val+'|'+$sentences_hash_val}) MATCH (s:Section {key:$doc_url_hash_val+'|'+$parent_block_idx_val+'|'+$parent_hash_val}) MERGE (s)<-[:HAS_PARENT]-(c);",
        ]


        driver = GraphDatabase.driver(self.neo4j_url, database=self.neo4j_database, auth=(self.neo4j_user, self.neo4j_password))
        print("During Ingestion: ")
        print("Driver started")

        with driver.session() as session:
            cypher = ""

            # 1 - Create Document node
            doc_url_val = doc_location
            doc_url_hash_val = hashlib.md5(doc_url_val.encode("utf-8")).hexdigest()

            cypher = cypher_pool[0]
            session.run(cypher, doc_url_hash_val=doc_url_hash_val, doc_url_val=doc_url_val)

            # 2 - Create Section nodes
            
            print("Starting section ingestion")
            
            countSection = 0
            for sec in doc.sections():
                sec_title_val = sec.title
                sec_title_hash_val = hashlib.md5(sec_title_val.encode("utf-8")).hexdigest()
                sec_tag_val = sec.tag
                sec_level_val = sec.level
                sec_page_idx_val = sec.page_idx
                sec_block_idx_val = sec.block_idx

                # MERGE section node
                if sec_tag_val != 'table':
                    cypher = cypher_pool[1]
                    session.run(cypher, page_idx_val=sec_page_idx_val
                                    , title_hash_val=sec_title_hash_val
                                    , title_val=sec_title_val
                                    , tag_val=sec_tag_val
                                    , level_val=sec_level_val
                                    , block_idx_val=sec_block_idx_val
                                    , doc_url_hash_val=doc_url_hash_val
                                )

                    # Link Section with a parent section or Document

                    sec_parent_val = str(sec.parent.to_text())

                    if sec_parent_val == "None":    # use Document as parent

                        cypher = cypher_pool[2]
                        session.run(cypher, page_idx_val=sec_page_idx_val
                                        , title_hash_val=sec_title_hash_val
                                        , doc_url_hash_val=doc_url_hash_val
                                        , block_idx_val=sec_block_idx_val
                                    )

                    else:   # use parent section
                        sec_parent_title_hash_val = hashlib.md5(sec_parent_val.encode("utf-8")).hexdigest()
                        sec_parent_page_idx_val = sec.parent.page_idx
                        sec_parent_block_idx_val = sec.parent.block_idx

                        cypher = cypher_pool[3]
                        session.run(cypher, page_idx_val=sec_page_idx_val
                                        , title_hash_val=sec_title_hash_val
                                        , block_idx_val=sec_block_idx_val
                                        , parent_page_idx_val=sec_parent_page_idx_val
                                        , parent_title_hash_val=sec_parent_title_hash_val
                                        , parent_block_idx_val=sec_parent_block_idx_val
                                        , doc_url_hash_val=doc_url_hash_val
                                    )

                countSection += 1
            print("sections ingested")
            

            
            # ------- Continue within the blocks -------
            # 3 - Create Chunk nodes from chunks
            print("Starting chunk ingestion")
            countChunk = 0
            for chk in doc.chunks():

                chunk_block_idx_val = chk.block_idx
                chunk_page_idx_val = chk.page_idx
                chunk_tag_val = chk.tag
                chunk_level_val = chk.level
                chunk_sentences = "\n".join(chk.sentences)

                # MERGE Chunk node
                if chunk_tag_val != 'table':
                    chunk_sentences_hash_val = hashlib.md5(chunk_sentences.encode("utf-8")).hexdigest()

                    # Create embedding for the chunk
                    chunk_embedding = self.embed_model.embed_text(chunk_sentences)

                    # MERGE chunk node
                    cypher = cypher_pool[4]
                    session.run(cypher, sentences_hash_val=chunk_sentences_hash_val
                                    , sentences_val=chunk_sentences
                                    , block_idx_val=chunk_block_idx_val
                                    , page_idx_val=chunk_page_idx_val
                                    , tag_val=chunk_tag_val
                                    , level_val=chunk_level_val
                                    , doc_url_hash_val=doc_url_hash_val
                                    , embedding_val=chunk_embedding
                                )
                
                    # Link chunk with a section
                    # Chunk always has a parent section 

                    chk_parent_val = str(chk.parent.to_text())
                    
                    if chk_parent_val != "None":
                        chk_parent_hash_val = hashlib.md5(chk_parent_val.encode("utf-8")).hexdigest()
                        chk_parent_page_idx_val = chk.parent.page_idx
                        chk_parent_block_idx_val = chk.parent.block_idx

                        cypher = cypher_pool[5]
                        session.run(cypher, sentences_hash_val=chunk_sentences_hash_val
                                        , block_idx_val=chunk_block_idx_val
                                        , parent_hash_val=chk_parent_hash_val
                                        , parent_block_idx_val=chk_parent_block_idx_val
                                        , doc_url_hash_val=doc_url_hash_val
                                    )

                    countChunk += 1
            
            print(f'\'{doc_url_val}\' Done! Summary: ')
            print('#Sections: ' + str(countSection))
            print('#Chunks: ' + str(countChunk))

        driver.close()
        
        return "Successul"

