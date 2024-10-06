import azure.functions as func
import logging
import visualize
import gridtools as gt
from io import BytesIO

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    lat, lon, maidenhead, maidensquare, output_file = None, None, None, None, None

    try:
        lat = req.form.get('lat')
        lon = req.form.get('lon')
        maidenhead = req.form.get('maidenhead')
        if maidenhead is not None and len(maidenhead) > 0:
            maidensquare = gt.Grid(maidenhead)
            lat = maidensquare.lat
            lon = maidensquare.long
        else:
            lat, lon = 0, 0
            
        for input_file in req.files.values():
            filename = input_file.filename
            contents = input_file.stream.read()
            output_file = visualize.build_map(contents, lat, lon)
            print(str(input_file))
            
    except Exception as exc:
        return func.HttpResponse(
            "Failed to open file with given inputs. Got exception: " + str(exc) + '\nCheck your inputs and try again. \
                ' + '\nReceived gridsquare: ' + str(maidenhead) + '\nReceived lat: ' + str(lat) + '\nReceived lon: ' + str(lon),
            status_code = 400
        )


    try:
        if output_file:
            f = BytesIO()
            output_file.save(f, 'png')
            f = f.getvalue()
            return func.HttpResponse(f, mimetype='image/png')
        
        else:
            return func.HttpResponse(
                "Failed to generate an image. File contents were: " + str(output_file),
                status_code = 400
            )
        
    except Exception as e:
        return func.HttpResponse(
            "Failed to save image, got exception: " + str(e),
            status_code = 400
        )