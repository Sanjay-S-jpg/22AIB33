import json
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from logging_middleware import log
from datetime import datetime, timedelta
import uuid

shortened_links = {}

def get_shortcode():
    return str(uuid.uuid4())[:8]

@csrf_exempt
def create_short_url(request):
    if request.method != 'POST':
        log('error', 'handler', f'Invalid method: {request.method}. Only POST is accepted.')
        return JsonResponse({'error': 'Only POST method is allowed.'}, status=405)

    try:
        request_data = json.loads(request.body)
        long_url = request_data.get('url')
        validity_minutes = request_data.get('validity', 30)
        custom_shortcode = request_data.get('shortcode')

        if not long_url:
            log('error', 'handler', 'Malformed input: "url" field is missing.')
            return JsonResponse({'error': 'url is a required field.'}, status=400)

        shortcode_to_use = custom_shortcode
        if not shortcode_to_use:
            shortcode_to_use = get_shortcode()
            log('debug', 'service', 'Generating a unique shortcode for the URL.')
        else:
            log('debug', 'service', f'Custom shortcode "{shortcode_to_use}" was provided.')
            if shortcode_to_use in shortened_links:
                log('warn', 'db', f'Shortcode "{shortcode_to_use}" is already in use.')
                return JsonResponse({'error': 'Shortcode is already in use.'}, status=409)

        expiry_time = datetime.now() + timedelta(minutes=validity_minutes)
        
        link_record = {
            'original_url': long_url,
            'expiry_date': expiry_time,
            'creation_date': datetime.now(),
            'clicks': 0,
            'click_data': []
        }

        shortened_links[shortcode_to_use] = link_record
        log('info', 'handler', f'Successfully created short URL for: {long_url}')

        return JsonResponse({
            'shortLink': f'http://127.0.0.1:8000/{shortcode_to_use}',
            'expiry': expiry_time.isoformat()
        }, status=201)
    
    except json.JSONDecodeError:
        log('error', 'handler', 'Invalid JSON in request body.')
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        log('fatal', 'handler', f'An unexpected error occurred: {str(e)}')
        return JsonResponse({'error': 'An internal error occurred.'}, status=500)

def redirect_to_long_url(request, shortcode):
    log('info', 'handler', f'Received request to redirect shortcode: {shortcode}')
    
    link_record = shortened_links.get(shortcode)
    
    if not link_record:
        log('error', 'db', f'Shortcode not found: {shortcode}')
        return JsonResponse({'error': 'Shortcode not found.'}, status=404)
        
    if datetime.now() > link_record['expiry_date']:
        log('warn', 'handler', f'Shortcode has expired: {shortcode}')
        return JsonResponse({'error': 'Shortcode has expired.'}, status=410)

   
    link_record['clicks'] += 1
    link_record['click_data'].append({
        'timestamp': datetime.now().isoformat(),
        'source': request.META.get('HTTP_REFERER', 'Direct'),
        'location': 'Unknown'
    })

    log('info', 'service', f'Redirecting "{shortcode}" to "{link_record["original_url"]}"')
    
    return HttpResponseRedirect(link_record['original_url'])

def get_short_url_stats(request, shortcode):
    log('info', 'handler', f'Received GET request for stats on shortcode: {shortcode}')

    link_record = shortened_links.get(shortcode)
    
    if not link_record:
        log('error', 'db', f'Shortcode not found: {shortcode}')
        return JsonResponse({'error': 'Shortcode not found.'}, status=404)
    
    if datetime.now() > link_record['expiry_date']:
        log('warn', 'handler', f'Stats requested for an expired shortcode: {shortcode}')
        return JsonResponse({'error': 'Shortcode has expired.'}, status=410)

    stats_response = {
        'totalClicks': link_record['clicks'],
        'originalUrl': link_record['original_url'],
        'creationDate': link_record['creation_date'].isoformat(),
        'expiryDate': link_record['expiry_date'].isoformat(),
        'clickData': link_record['click_data']
    }

    log('info', 'handler', f'Successfully retrieved stats for shortcode: {shortcode}')
    return JsonResponse(stats_response, status=200)
