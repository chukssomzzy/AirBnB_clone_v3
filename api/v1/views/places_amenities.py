#!/usr/bin/python3

"""Does db depending task"""
from models import storage, storage_t
from flask import make_response, jsonify, abort
from api.v1.views import app_views


@app_views.route('/places/<place_id>/amenities', strict_slashes=False)
def get_place_amenities(place_id):
    """Depending on the storage engines list ids  or object"""
    place = storage.get('Place', place_id)
    if not place:
        abort(404)
    amenities = []
    if storage_t == 'db':
        amenities = [amenity.to_dict() for amenity in place.amenities]
    else:
        for id in place.amenity_ids:
            amenity = storage.get('Amenity', id)
            if amenity:
                amenities.append(amenity.to_dict())
    return jsonify(amenities)


@ app_views.route('/places/<place_id>/amenities/<amenity_id>',
                  methods=['DELETE'], strict_slashes=False)
def delete_place_amenity(place_id, amenity_id):
    """Takes a place_id and amenity_id and remove/delete depending on storage
    engine
    """
    place = storage.get('Place', place_id)
    if not place:
        abort(404)
    amenity = storage.get('Amenity', amenity_id)
    if not amenity:
        abort(404)
    if storage_t == 'db' and amenity in place.amenities:
        place.amenities.remove(amenity)
    elif storage_t != 'db' and amenity.id in place.amenity_ids:
        place.amenity_ids.remove(amenity.id)
    else:
        abort(404)
    storage.save()
    return make_response(jsonify({}), 200)


@ app_views.route('/places/<place_id>/amenities/<amenity_id>',
                  methods=['POST'], strict_slashes=False)
def post_place_amenity(place_id, amenity_id):
    """Attach a amenity to a place"""
    place = storage.get('Place', place_id)
    if not place:
        abort(404)
    amenity = storage.get('Amenity', amenity_id)
    if not amenity:
        abort(404)
    if storage_t == 'db' and amenity in place.amenities:
        return make_response(jsonify(amenity.to_dict()), 200)
    elif storage_t == 'db' and amenity.id in place.amenity_ids:
        return make_response(jsonify(amenity.to_dict()), 200)
    if storage_t == 'db':
        place.amenities.append(amenity)
    else:
        place.amenity_ids.append(amenity.id)
    storage.save()
    return make_response(jsonify(amenity.to_dict()), 201)
