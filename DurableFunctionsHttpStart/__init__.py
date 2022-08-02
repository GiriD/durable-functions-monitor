import logging
import azure.functions as func
import azure.durable_functions as df

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    client = df.DurableOrchestrationClient(starter)
    if not req.get_body():
        return func.HttpResponse("Missing message body.", status_code=400)
    
    input = req.get_json()

    # Input validation
    if 'city' not in input:
        return func.HttpResponse("Missing city in message body.", status_code=400)
    if 'alert_temperature' not in input:
        return func.HttpResponse("Missing alert_temperature in message body.", status_code=400)
    if 'phone_number' not in input:
        return func.HttpResponse("Missing phone_number in message body.", status_code=400)
    
    instance_id = await client.start_new(req.route_params["functionName"], None, input)

    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    return client.create_check_status_response(req, instance_id)