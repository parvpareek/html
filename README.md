# html

latest update:
there are still issues with the upload_pdf endpoint
get_section or something endpoint ( question generation) works just fine. Try it out by running utils.demo.py

api keys are in the .env file


```pip install nlm-ingestor
docker pull ghcr.io/nlmatics/nlm-ingestor:v0.1.6
docker run -p 5010:5001 ghcr.io/nlmatics/nlm-ingestor:v0.1.6```


cd to fastapi dir

``` pip install uvicorn fastapi ```

then run:

```uvicorn main:app --reload```


