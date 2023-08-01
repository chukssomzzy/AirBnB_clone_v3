#!/usr/bin/python3
"""Handles all default RESTFUL API actions for places"""

from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from models import storage
from models.place import Place


@app_views.route("/cities/<city_id>/places", strict_slashes=False)
def get_places_by_city_id(city_id):
    city = storage.get('City', city_id)
    """Get all places related to a city"""
    if not city:
        abort(404)
    return jsonify([place.to_dict() for place in city.places])


@app_views.route("/places/<place_id>", strict_slashes=False)
def get_places_by_id(place_id):
    """Get a place with the id"""
    place = storage.get('Place', place_id)
    if not place:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route("/places/<place_id>", methods=['DELETE'],
                 strict_slashes=False)
def delete_place_by_id(place_id):
    """Take an Id and delete a place identified by the id """
    place = storage.get('Place', place_id)
    if not place:
        abort(404)
    storage.delete(place)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route("/cities/<city_id>/places", methods=["POST"],
                 strict_slashes=False)
def post_city_place(city_id):
    """Takes a city id and post a place related to city"""
    city = storage.get('City', city_id)
    if not city:
        abort(404)
    if not request.get_json():
        abort(400, "Not a JSON")
    if "user_id" not in request.get_json():
        return make_response(jsonify({'error': 'Missing user_id'}), 400)
    user = storage.get('User', (request.get_json()).get('user_id'))
    if not user:
        abort(404)
    if "name" not in request.get_json():
        make_response(jsonify({'error': "Missing name"}))
    place_data = request.get_json()
    place_data['city_id'] = city_id
    place = Place(**place_data)
    place.save()
    return make_response(jsonify(place.to_dict()), 201)


@app_views.route("/places/<place_id>", methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """update a place identified by the place_id"""
    ignore_keys = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
    place = storage.get("Place", place_id)
    if not place:
        abort(404)
    if not request.get_json():
        return make_response(jsonify({'error': "Not a JSON"}), 400)
    for key, val in request.get_json().items():
        if key not in ignore_keys:
            setattr(place, key, val)
    place.save()
    return make_response(jsonify(place.to_dict()), 200)


@app_views.route("/places_search", methods=['POST'], strict_slashes=False)
def search_places():
    """search places with params from request.get_json"""
    json_key = request.get_json()
    places = set()
    if not request.is_json:
        abort(400, "Not a JSON")
    if not len(json_key) or all(len(val) == 0 for val in
                                [val for key, val in
                                 json_key.items()
                                 if key != "amenities"]):
        places = {place for place in json_key.values()}
    for key, val in json_key.items():
        for id in val:
            if key == "states":
                state = storage.get('State', id)
                if state:
                    for city in state.cities:
                        for place in city.places:
                            places.add(place)
            if key == "cities":
                city = storage.get("City", id)
                if city:
                    for place in city.places:
                        places.add(place)
    if json_key.get("amenities"):
        places_copy = places.copy()
        for place in places_copy:
            if not all(storage.get('Amenity', id) in place.amenities for id in
                       json_key['amenities']):
                places.remove(place)
    return jsonify([place.to_dict() for place in places])
