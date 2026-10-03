import boto3
import csv
import io
import urllib.parse


# Create an S3 client that Lambda will use to read and write files.
s3 = boto3.client("s3")




def lambda_handler(event, context):
    print("CareBridge processing started.")


    # Get the bucket name and object key from the S3 event.
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"]
    )


    print(f"Source bucket: {bucket}")
    print(f"Processing file: {key}")


    # Read the CSV file from the raw zone in S3.
    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )


    csv_content = response["Body"].read().decode("utf-8")


    # Convert the CSV text into rows that Python can process.
    reader = csv.DictReader(io.StringIO(csv_content))


    department_revenue = {}
    record_count = 0
    completed_count = 0


    # Process each hospital visit.
    for row in reader:
        record_count += 1


        # Revenue is recognized only for completed visits.
        if row["visit_status"] == "Completed":
            completed_count += 1


            department = row["department"]
            consultation_fee = int(row["consultation_fee"])


            department_revenue[department] = (
                department_revenue.get(department, 0)
                + consultation_fee
            )


    print(f"Total records processed: {record_count}")
    print(f"Completed visits processed: {completed_count}")


    # Create the processed CSV in memory.
    output = io.StringIO()


    writer = csv.writer(output)
    writer.writerow(["department", "total_revenue"])


    for department, revenue in sorted(
        department_revenue.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        writer.writerow([department, revenue])


    # Write the processed result back to S3.
    output_key = "processed/department_revenue.csv"


    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=output.getvalue(),
        ContentType="text/csv"
    )


    print(f"Processed output written to: {output_key}")
    print("CareBridge processing completed successfully.")


    return {
        "statusCode": 200,
        "body": {
            "message": "CareBridge healthcare data processed successfully.",
            "source_file": key,
            "output_file": output_key,
            "records_processed": record_count,
            "completed_visits": completed_count
        }
    }