import json
from datetime import datetime
from flask import Flask, request, g
from flask_restful import Api, abort, reqparse, Resource

from models import Annotation, db


app = Flask(__name__)
app.config['ERROR_404_HELP'] = False
api = Api(app)


@app.before_request
def before_request():
    g.db = db
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


parser = reqparse.RequestParser()
parser.add_argument('url', type=str, required=True)


class AnnotationListResource(Resource):
    def get(self):
        args = parser.parse_args()
        url = args.get('url')

        annotations = Annotation.select().where(
            Annotation.url == url
        ).order_by(Annotation.created)

        return [x.serialize() for x in annotations]

    def post(self):
        args = parser.parse_args()
        url = args.get('url')

        data = request.json

        annotation = Annotation(
            url=url,
            data=json.dumps(data),
            created=datetime.now()
        )
        annotation.save()
        return annotation.serialize()


class AnnotationResource(Resource):
    def get(self, annotation_id):
        try:
            annotation = Annotation.get(
                Annotation.id == annotation_id
            )
        except Annotation.DoesNotExist:
            abort(404, message="Annotation {} doesn't exist".format(annotation_id))
        return annotation.serialize()

    def put(self, annotation_id):
        try:
            annotation = Annotation.get(
                Annotation.id == annotation_id,
            )
        except Annotation.DoesNotExist:
            abort(404, message="Annotation {} doesn't exist".format(annotation_id))

        data = request.json
        annotation.data = json.dumps(data)
        annotation.save()

        return annotation.serialize()


api.add_resource(AnnotationListResource, '/')
api.add_resource(AnnotationResource, '/<annotation_id>')
