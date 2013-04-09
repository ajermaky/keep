import json

from bson import ObjectId
from datetime import datetime
from numpy import linspace

from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from backend.db import db, dehydrate_survey
from privacy.map import privatize

from pyxform.xls2json import SurveyReader

from .forms import NewRepoForm


def new_repo( request ):
    # Handle XForm upload
    if request.method == 'POST':

        form = NewRepoForm( request.POST, request.FILES )

        # Check for a valid XForm and parse the file!
        if form.is_valid():

            # Check that this form name isn't already taken by the user
            form_exists = db.survey.find( { 'name': form.cleaned_data['name'],
                                            'user': request.user.id } )

            if form_exists.count() != 0:
                errors = form._errors.setdefault( 'name', ErrorList() )
                errors.append( 'Repository already exists with this name' )
            else:
                # Parse the file and store into our database
                survey = SurveyReader( request.FILES[ 'xform_file' ] )

                if len( survey._warnings ) > 0:
                    print 'Warnings parsing xls file!'

                data = survey.to_json_dict()

                # Basic form name/description
                data[ 'name' ] = form.cleaned_data[ 'name' ]
                data[ 'description' ] = form.cleaned_data[ 'desc' ]

                # Needed for xform formatting
                data[ 'title' ]       = form.cleaned_data[ 'name' ]
                data[ 'id_string' ]   = form.cleaned_data[ 'name' ]

                # Is this form public?
                data[ 'public' ] = form.cleaned_data[ 'privacy' ] == 'public'

                # Store who uploaded this form
                data[ 'user' ]      = request.user.id

                # Store when this form was uploaded
                data[ 'uploaded' ]  = datetime.now()

                db.survey.insert( data )

                return HttpResponseRedirect( '/' )

    else:
        form = NewRepoForm()

    return render_to_response( 'new.html', { 'form': form },
                               context_instance=RequestContext(request) )


def delete_repo( request, repo_id ):

    survey = db.survey.find_one( { '_id': ObjectId( repo_id ) },
                                 { 'user': True } )

    if survey[ 'user' ] != request.user.id:
        return HttpResponse( 'Unauthorized', status=401 )

    db.survey.remove( { '_id': ObjectId( repo_id ) } )
    db.survey_data.remove( { 'survey': ObjectId( repo_id ) } )

    return HttpResponseRedirect( '/' )


@csrf_exempt
@require_POST
def toggle_public( request, repo_id ):
    '''
        Toggle's a data repo's "publicness". Only the person who owns the form
        is allowed to make such changes to the form settings.
    '''

    # Find a survey, only looking for the user field
    survey = db.survey.find_one( { '_id': ObjectId( repo_id ) },
                                 { 'user': True, 'public': True } )

    # Check if the owner of the survey matches the user who is logged in
    if survey[ 'user' ] != request.user.id:
        return HttpResponse( 'Unauthorized', status=401 )

    if 'public' in survey:
        survey[ 'public' ] = not survey[ 'public' ]
    else:
        survey[ 'public' ] = True

    db.survey.update( { '_id': ObjectId( repo_id ) },
                      { '$set': { 'public': survey[ 'public' ] } } )

    return HttpResponse( json.dumps( { 'success': True,
                                       'public': survey[ 'public' ] } ),
                         mimetype='application/json' )


@require_GET
def webform( request, repo_name ):
    '''
        Simply grab the survey data and send it on the webform. The webform
        will handle rendering and submission of the final data to the server.
    '''
    repo = db.survey.find_one( { 'name': repo_name } )

    if repo is None:
        return HttpResponse( status=404 )

    repo_user = get_object_or_404( User, id=repo[ 'user' ] )

    return render_to_response(  'get.html',
                                { 'repo': repo,
                                  'repo_user': repo_user,
                                  'repo_id': str( repo[ '_id' ] ) },
                                context_instance=RequestContext( request ) )


@require_GET
def repo_viz( request, username, repo_name ):

    user = get_object_or_404( User, username=username )

    # Looking our own viz or someone's public repo?
    is_other_user = request.user.username != username

    repo = db.survey.find_one({ 'name': repo_name, 'user': user.id })

    if repo is None:
        return HttpResponse( status=404 )

    # Check to see if the user has access to view this survey
    if not repo.get( 'public', False ) and is_other_user:
        return HttpResponse( 'Unauthorized', status=401 )

    # Grab the data for this repository
    data = db.survey_data.find( {'survey': ObjectId( repo[ '_id' ] )} )
    data = dehydrate_survey( data )

    # Is some unknown user looking at this data?
    if is_other_user:
        # Does this data have any geo data?
        has_geo = False
        geo_index = None
        for field in repo[ 'children' ]:
            if field[ 'type' ] == 'geopoint':
                has_geo = True
                geo_index = field[ 'name' ]
                break

        # Great! We have geopoints, let's privatize this data
        if has_geo:

            xbounds     = [ None, None ]
            ybounds     = [ None, None ]
            fuzzed_data = []

            for datum in data:

                geopoint = datum[ 'data' ][ geo_index ].split( ' ' )
                point = ( float( geopoint[0] ), float( geopoint[1] ) )

                if xbounds[0] is None or point[0] < xbounds[0]:
                    xbounds[0] = point[0]

                if xbounds[1] is None or point[0] > xbounds[1]:
                    xbounds[1] = point[0]

                if ybounds[0] is None or point[1] < ybounds[0]:
                    ybounds[0] = point[1]

                if ybounds[1] is None or point[1] > ybounds[1]:
                    ybounds[1] = point[1]

                fuzzed_data.append( point )

            # Split the xbounds in a linear
            xbounds = linspace( xbounds[0], xbounds[1], num=20 )
            ybounds = linspace( ybounds[0], ybounds[1], num=20 )

            fuzzed_data = privatize( points=fuzzed_data,
                                     xbounds=xbounds,
                                     ybounds=ybounds )
            data = []
            for datum in fuzzed_data:
                data.append( {
                    'data':
                    {geo_index: ' '.join( [ str( x ) for x in datum ] )}})

    return render_to_response( 'visualize.html',
                               { 'repo': repo,
                                 'sid': repo[ '_id' ],
                                 'data': json.dumps( data ),
                                 'is_other_user': is_other_user,
                                 'account': user},
                               context_instance=RequestContext(request) )


@require_GET
def map_visualize( request ):
    return render_to_response( 'map_visualize.html',
                               context_instance=RequestContext(request) )
