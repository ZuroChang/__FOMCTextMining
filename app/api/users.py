from flask import jsonify
from . import api
from ..models import User


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


#import requests, json
#
#r=requests.get('http://localhost:5000/api/v1/users/2',auth=('zurochang@gmail.com','123qqq'))
#Data=json.loads(r.text)



