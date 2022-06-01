#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
from wsgiref import validate
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from models import *
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data =[]
  venue_details = Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()

  for exact_venue in venue_details:
    locations = Venue.query.with_entities(Venue.city, Venue.state).all()

    venues_list=[]
  
    for location in locations:
      data.append({
        'city': location[0],
        'state': location[1],
        'venues': venues_list
      })

  for exact_venue in venue_details:
    print(exact_venue)
    for venue_data in data:
      if venue_data['city'] == exact_venue.city and venue_data['state'] == exact_venue.state:
        num_upcoming_shows = len(Show.query.join(Venue).filter(Venue.id == venue_details.id, Show.start_time > datetime.utcnow()))
        venues_list.append(
          {
            "id": venue_details.id,
            "name": venue_details.name,
            "num_upcoming_shows": num_upcoming_shows
          }
        )
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = request.form.get('search_term', '')

  search_results = Venue.query.filter(
      Venue.name.ilike('%' + search_term + '%')).all()

  search_results_count = len(search_results)
  artist_data = []

  current_time = datetime.utcnow()
  future_shows = len(Show.query.filter(
      Show.venue_id == search_result.id, Show.start_time > current_time).all())

  for search_result in search_results:

    response = {
        "count": search_results_count,
        "data": artist_data,
    }

    artist_data.append({
        "id": search_result.id,
        "name": search_result.name,
        "num_upcoming_shows": future_shows,
    })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.get(venue_id)
  if venue:
    print(venue)

    current_time = datetime.utcnow()

    old_shows_query = Show.query.join(Venue).filter(
        Venue.id == venue_id, Show.start_time <= current_time).all()
    new_shows_query = Show.query.join(Venue).filter(
        Venue.id == venue_id, Show.start_time > current_time).all()
    
    new_shows = new_shows_query
    old_shows = old_shows_query
    return render_template('pages/show_artist.html', venue=venue, upcoming_shows=new_shows, past_shows=old_shows)
  else:
    return render_template('errors/404.html')

  
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  if VenueForm(request.form).validate():
    try:
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      address = request.form.get('address'),
      phone = request.form.get('phone'),
      image_link = request.form.get('image_link'),
      genres = request.form.getList('genres'),
      facebook_link = request.form.get('facebook_link'),
      website_link = request.form.get('website_link'),
      seeking_talent = request.form.get('seeking_talent'),
      seeking_description = request.form.get('seeking_description'),
      
      new_venue = Venue(name=name, city=city, state=state, phone=phone, address=address, 
      genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, 
      seeking_talent=seeking_talent, seeking_description=seeking_description)

      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return redirect(url_for('index'))
    except:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    flash('Sorry, your details were not properly validated. Please check the form and try again ')
    return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    
    try:
      Venue.query.filter(Venue.id == venue_id).delete()

      db.session.commit()
      flash('Venue ' + Venue.name + ' was successfully DELETED!')
      return redirect(url_for('index'))
    except:
      flash('An error occurred. Venue ' +
            Venue.name + ' could not be DELETED.')
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term', '')

  search_results = Artist.query.filter(
      Artist.name.ilike('%' + search_term + '%')).all()
  
  search_results_count = len(search_results)
  artist_data = []

  current_time = datetime.utcnow()
  future_shows = len(Show.query.filter(
      Show.artist_id == search_result.id, Show.start_time > current_time).all())
  
  for search_result in search_results:
    
    response = {
        "count": search_results_count,
        "data": artist_data,
    }

    artist_data.append({
      "id": search_result.id,
      "name": search_result.name,
      "num_upcoming_shows": future_shows,
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  if artist:
    print(artist)
    
    current_time = datetime.utcnow()

    old_shows_query = Show.query.join(Artist).filter(
        Artist.id == artist_id, Show.start_time <= current_time).all()
    new_shows_query = Show.query.join(Artist).filter(
        Artist.id == artist_id, Show.start_time > current_time).all()
    
    new_shows = new_shows_query
    old_shows = old_shows_query
    return render_template('pages/show_artist.html', artist=artist, upcoming_shows=new_shows, past_shows=old_shows)
  else:
    return render_template('errors/404.html')
  
  
  
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if artist:
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website_link
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  else:
    return render_template('errors/404.html')

  # TODO: populate form with fields from artist with ID <artist_id>

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form)
  if form.validate():
    try:
      artist.name = request.form.get('name'),
      artist.city = request.form.get('city'),
      artist.state = request.form.get('state'),
      artist.phone = request.form.get('phone'),
      artist.genres = request.form.getList('genres'),
      artist.facebook_link = request.form.get('facebook_link'),
      artist.image_link = request.form.get('image_link'),
      artist.website_link = request.form.get('website_link'),
      artist.seeking_venue = request.form.get('seeking_venue'),
      artist.seeking_description = request.form.get('seeking_description'),

      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
      return redirect(url_for('show_artist', artist_id=artist_id))
    except:
      flash('An error occurred. Artist ' +
            request.form['name'] + ' could not be updated.')
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    flash('An error occurred. Please check the form and try again ')
    return redirect(url_for('show_artist', artist_id=artist_id))

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Artist.query.get(venue_id)
  if venue:
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website_link
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  else:
    return render_template('errors/404.html')
  
  # # TODO: populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  if form.validate():
    try:
      venue.name = request.form.get('name'),
      venue.city = request.form.get('city'),
      venue.state = request.form.get('state'),
      venue.phone = request.form.get('phone'),
      venue.genres = request.form.getList('genres'),
      venue.facebook_link = request.form.get('facebook_link'),
      venue.image_link = request.form.get('image_link'),
      venue.website_link = request.form.get('website_link'),
      venue.seeking_talent = request.form.get('seeking_talent'),
      venue.seeking_description = request.form.get('seeking_description'),

      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
      return redirect(url_for('show_venue', venue_id=venue_id))
    except:
      flash('An error occurred. Artist ' +
            request.form['name'] + ' could not be updated.')
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    flash('An error occurred. Please check the form and try again ')
    return redirect(url_for('show_venue', venue_id=venue_id))

  # # TODO: take values from the form submitted, and update existing
  # # venue record with ID <venue_id> using the new attributes
  # return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  if form.validate():
    try:
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      genres = request.form.getList('genres'),
      facebook_link = request.form.get('facebook_link'),
      image_link = request.form.get('image_link'),
      website_link = request.form.get('website_link'),
      seeking_venue = request.form.get('seeking_venue'),
      seeking_description = request.form.get('seeking_description'),
      
      new_artist = Artist(name=name, city=city, state=state, phone=phone,
      genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, 
      seeking_venue=seeking_venue, seeking_description=seeking_description)

      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return redirect(url_for('index'))
    except:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    flash('Sorry, your details were not properly validated. Please check the form and try again ')
    return redirect(url_for('index'))
      
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)
  
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm(request.form)
  if form.validate():
    try:
      artist_id = request.form.get('artist_id')
      venue_id = request.form.get('venue_id')
      start_time = request.form.get('start_time')

      show=Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
      return redirect(url_for('index'))
    except:
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
      return redirect(url_for('index'))
  else:
    flash('Sorry, your details were not properly validated. Please check the form and try again ')
    return redirect(url_for('index'))




@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
