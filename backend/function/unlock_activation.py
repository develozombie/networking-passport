import json
import os
import uuid

import boto3
from botocore.exceptions import ClientError
from utils import generate_http_response

# Inicializamos el cliente de DynamoDB
dynamodb = boto3.client("dynamodb")

# Definir el nombre de la tabla
table_name = os.environ.get("DYNAMODB_TABLE_NAME")
index_name = os.environ.get("INDEX_NAME")


def lambda_handler(event, context):
    # Obtener el short_id y el valor desde la solicitud HTTP
    try:
        short_id = event["queryStringParameters"]["short_id"]
        value = event["queryStringParameters"][
            "value"
        ]  # Esto puede ser email o últimos 6 dígitos del teléfono
    except KeyError:
        return generate_http_response(400, {"error": "short_id and value are required"})

    try:
        # Realizamos el query usando el índice global secundario (GSI)
        response = dynamodb.query(
            TableName=table_name,
            IndexName=index_name,
            KeyConditionExpression="short_id = :sid",
            ExpressionAttributeValues={":sid": {"S": short_id}},
        )

        # Revisar si el ítem existe
        if "Items" not in response or len(response["Items"]) == 0:
            return generate_http_response(404, {"error": "short_id not found"})

        # Obtener la información de contacto
        item = response["Items"][0]
        contact_info = item.get("contact_information", {}).get("M", {})

        email = contact_info.get("email", {}).get("S")
        phone = contact_info.get("phone", {}).get("S")

        # Validar si el valor corresponde al correo o los últimos 6 dígitos del teléfono
        if value == email or (phone and phone[-6:] == value):
            # Si es válido, generar un UUIDv4 como unlock_key
            unlock_key = str(uuid.uuid4())

            # Guardar el unlock_key en la base de datos, agregándolo al registro del usuario
            try:
                dynamodb.update_item(
                    TableName=table_name,
                    Key={"PK": item["PK"], "SK": item["SK"]},
                    UpdateExpression="SET unlock_key = :unlock_key",
                    ExpressionAttributeValues={":unlock_key": {"S": unlock_key}},
                )

                # Retornar el unlock_key generado
                return generate_http_response(200, {"unlock_key": unlock_key})

            except ClientError as e:
                print(f"An error occurred when updating unlock_key: {e}")
                return generate_http_response(
                    500, {"error": "Error updating unlock_key in DynamoDB"}
                )
        else:
            # Si el valor no coincide con el correo o los últimos 6 dígitos del teléfono
            return generate_http_response(
                400, {"error": "Invalid email or phone number"}
            )

    except ClientError as e:
        print(f"An error occurred: {e}")
        return generate_http_response(500, {"error": "Error accessing DynamoDB"})
