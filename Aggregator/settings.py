import os
if "bucket" in os.environ:
    BUCKET = os.environ["bucket"]
else:
    BUCKET = "sdd-s3-basebucket"

#BUCKET = "sdd-s3-bucket"
