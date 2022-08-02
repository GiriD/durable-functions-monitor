from datetime import timedelta
from dateutil import tz
import azure.functions as func
import azure.durable_functions as df

def orchestrator_function(context: df.DurableOrchestrationContext):
    # Get input passed to starter function
    input = context.get_input()

    # Get latitude and longitude information about the input city
    lat_lon = yield context.call_activity('GetLatLon', input['city'])

    # Stop Durable function after 5 days
    expiry_time = context.current_utc_datetime + timedelta(days=5)
    
    while context.current_utc_datetime < expiry_time:
        # Get the current temperature for the city
        temperature = yield context.call_activity("GetTemp", lat_lon)

        # If current temperature is equal to or above the alert threshold, text the provided phone number
        if temperature >= input['alert_temperature']:
            status = "Alert temperature threshold reached at " + convert_local_timestamp(context.current_utc_datetime) + ". Durable Function stopped."
            context.set_custom_status(status)
            
            # Message content
            message_content = {}
            message_content['phone_number'] = input['phone_number']
            message_content['body'] = "Alert temperature threshold reached at " + convert_local_timestamp(context.current_utc_datetime)
            
            yield context.call_activity("SendAlert", message_content)

            # Stop the durable function after threshold reached
            break
        else:
            # Schedule the next check time based on the temperature difference
            if input['alert_temperature'] - temperature > 10:
                # the difference between current and threshold is greater than 10 degrees, check again after 4 hrs
                next_check_minutes = 240
            elif input['alert_temperature'] - temperature > 5:
                # the difference between current and threshold is between 5 and 10 degrees, check again after 3 hrs
                next_check_minutes = 180
            elif input['alert_temperature'] - temperature > 2:
                # the difference between current and threshold is between 3 and 5 degrees, check again after 2 hrs
                next_check_minutes = 120 
            elif input['alert_temperature'] - temperature > 1:
                # the difference between current and threshold is between 1 and 2 degrees, check again after 1 hr
                next_check_minutes = 60
            else:
                # the difference between current and threshold less than a degree, check again after 10 min
                next_check_minutes = 10

            next_check = context.current_utc_datetime + timedelta(minutes=next_check_minutes)

            # Reporting the current status
            status = "Current temperature is " + str(temperature) + " deg celcius which is below the alert threshold. Next check at: " + convert_local_timestamp(next_check)
            context.set_custom_status(status)

            yield context.create_timer(next_check)

    return "Alert temperature threshold reached at " + convert_local_timestamp(context.current_utc_datetime)

# Convert UTC to local timestamp
def convert_local_timestamp(utc_timestamp) -> str:
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    current_utc = utc_timestamp.replace(tzinfo=from_zone)
    current_local_datetime = current_utc.astimezone(to_zone)
    date_format = "%d %b %Y %I:%M:%S %p %Z"
    return current_local_datetime.strftime(date_format)

main = df.Orchestrator.create(orchestrator_function)