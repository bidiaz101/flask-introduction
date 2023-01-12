from flask import Flask, request
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) # flask boilerplate
api = Api(app) # wraps app in API
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class VideoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    views = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

db.create_all()

video_put_args = reqparse.RequestParser() # validates args
video_put_args.add_argument("name", type=str, help="Video needs a name", required=True)
video_put_args.add_argument("views", type=int, help="Video needs views", required=True)
video_put_args.add_argument("likes", type=int, help="Video needs likes", required=True)

video_patch_args = reqparse.RequestParser()
video_patch_args.add_argument("name", type=str)
video_patch_args.add_argument("views", type=int)
video_patch_args.add_argument("likes", type=int)

resource_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "views": fields.Integer,
    "likes": fields.Integer
}

class Video(Resource): # class inherits from resource todo: google resource
    @marshal_with(resource_fields) # used to serialize to JSON
    def get(self, video_id):
        print(self, video_id)
        result = VideoModel.query.filter_by(id=video_id).first() # can also use .get({"id": video_id})
        if not result:
            abort(404, message="could not find video with that id")
        
        return result

    @marshal_with(resource_fields)
    def put(self, video_id):
        result = VideoModel.query.get({"id": video_id})
        if result:
            abort(409, message="video id taken")
        
        args = video_put_args.parse_args()
        video = VideoModel(id=video_id, name=args["name"], views=args["views"], likes=args["likes"])
        db.session.add(video)
        db.session.commit() # makes changes to the db permanent
        return video, 201

    @marshal_with(resource_fields)
    def patch(self, video_id):
        result = VideoModel.query.get({"id": video_id})
        if not result:
            abort(404, message="Video not found")
        else:
            args = video_patch_args.parse_args()
            if args['name']:
                result.name = args['name']
            if args['views']:
                result.views = args['views']
            if args['likes']:
                result.likes = args['likes']
        
        db.session.commit()
        return result
    
    @marshal_with(resource_fields)
    def delete(self, video_id):
        result = VideoModel.query.get({"id": video_id})
        if not result:
            abort(404, message="Video not found")
        else:
            db.session.delete(result)
            db.session.commit()
            return "", 201


api.add_resource(Video, "/video/<int:video_id>")

if __name__ == "__main__": # used to start server/app
    app.run(debug=True) # debug mode, logs info, remove in prod env
