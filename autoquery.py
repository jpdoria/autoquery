import json
import os
import sys
import time
import boto3


def execute():
    """
    Run the query against the Athena database and get the data from the previous month. The results will be stored on an S3 bucket.
    These environment variables should be available: ATHENA_DATABASE, ATHENA_TABLE, AWS_REGION, PROJECT_PREFIX, and S3_BUCKET.
    """
    query = f"""\
    SELECT date,
        log_processed.path,
        log_processed.code,
        log_processed.agent,
        log_processed.proxy_upstream_name,
        log_processed.request_time,
        log_processed.upstream_response_time
    FROM "{os.environ["ATHENA_DATABASE"]}"."{os.environ["ATHENA_TABLE"]}"
    WHERE "$path" LIKE '%{os.environ["PROJECT_PREFIX"]}%'
        AND log_processed.path != ''
        AND stream = 'stdout'
        AND date_format(from_iso8601_timestamp(date), '%Y-%m') = date_format(current_date - interval '1' month, '%Y-%m')
    ORDER BY date ASC
    """

    client = boto3.client("athena", region_name=os.environ["AWS_REGION"])
    query_execution_id = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": os.environ["ATHENA_DATABASE"]},
        ResultConfiguration={"OutputLocation": os.environ["S3_BUCKET"]},
    )["QueryExecutionId"]

    # Waiter workaround
    # https://github.com/guardian/athena-cli/blob/master/athena_cli.py#L37-L42
    while True:
        stats = client.get_query_execution(QueryExecutionId=query_execution_id)
        status = stats["QueryExecution"]["Status"]["State"]

        if status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            print(json.dumps(stats, indent=4, default=str))
            break

        time.sleep(0.2)  # 200ms


def main():
    """
    Main func.
    """
    execute()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Goodbye!\n")
        sys.exit(1)
