# About

autoquery — run queries against the Athena database using the cronjob to get the request and response times from the previous day, save the results in CSV format, and upload it to S3.

# Prep

## IAM — Athena and S3 policies

```bash
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "autoquery00",
            "Effect": "Allow",
            "Action": [
                "athena:StartQueryExecution",
                "athena:GetQueryExecution"
            ],
            "Resource": "*"
        },
        {
            "Sid": "autoquery01",
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::my_bucket", # change me
                "arn:aws:s3:::my_bucket/*" # change me
            ]
        }
    ]
}
```

## Docker


```bash
# Retrieve an authentication token and authenticate your Docker client to your registry. Use the AWS CLI:
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 012345678901.dkr.ecr.us-east-1.amazonaws.com

# Build your Docker image using the following command. You can skip this step if your image is already built:
docker build -t autoquery .

# After the build completes, tag your image so you can push the image to this repository:
docker tag autoquery:latest 012345678901.dkr.ecr.us-east-1.amazonaws.com/autoquery:latest

# Run the following command to push this image to your newly created AWS repository:
docker push 012345678901.dkr.ecr.us-east-1.amazonaws.com/autoquery:latest
```

# Usage

```bash
# Open the cronjob template
vim k8s_cronjob.yaml

# Make some changes if necessary
apiVersion: v1
kind: Namespace
metadata:
  name: autoquery
---
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: client-dev # change me
  namespace: autoquery
spec:
  schedule: "0 0 1 * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 0
  failedJobsHistoryLimit: 0
  jobTemplate:
    spec:
      backoffLimit: 0
      template:
        spec:
          containers:
            - name: client-dev # change me
              image: autoquery # change me
              imagePullPolicy: IfNotPresent
              env:
                - name: ATHENA_DATABASE
                  value: dummy_db # change me
                - name: ATHENA_TABLE
                  value: dummy_table # change me
                - name: AWS_REGION
                  value: us-east-1 # change me
                - name: PROJECT_PREFIX
                  value: client-dev # change me
                - name: S3_BUCKET
                  value: s3://dummy_bucket # change me
                # - name: AWS_ACCESS_KEY_ID # for local testing (minikube)
                #  value: # change me
                # - name: AWS_SECRET_ACCESS_KEY # for local testing (minikube)
                #  value: # change me
          restartPolicy: Never

# Save and exit from the editor and apply it to K8s cluster.
kubectl apply -f k8s_cronjob.yaml
```

# How to trigger the cronjob manually

```bash
kubectl -n autoquery create job --from=cronjob/<cronjob_name> <job_name>
```