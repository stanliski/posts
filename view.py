from models import Post, Label, LabelRelationship, User, datebase
from flask import Flask, request, render_template, jsonify
from werkzeug.exceptions import MethodNotAllowed, BadRequest, InternalServerError
from peewee import IntegrityError
from app import app
from conf import PER_PAGE_NUM
import json


@app.route("/", methods=['GET'])
@app.route("/blogs", methods=['GET'])
def post_index():
    """
    Get posts which status equals Public.
    :return: public_posts
    """
    if not request.method == 'GET':
        return MethodNotAllowed

    page = request.args.get('page', 1, type=int)
    public_posts = (Post.select()
                    .where(Post.status == 0)
                    .order_by(Post.timestamp.desc()).paginate(page, PER_PAGE_NUM))

    public_labels = Label.select()
    return render_template("index.html", posts=public_posts,
                           total=get_total_page(), page=page, labels=public_labels)


@app.route("/api/blogs", methods=['POST'])
def json_post_index():
    """
    Get posts which status equals Public by json format.
    :return:
    """
    if not request.method == 'POST':
        return MethodNotAllowed
    try:
        public_posts = Post.select()
        json_posts = []
        for post in public_posts:
            print post.to_json()
            json_posts.append(post.to_json())
    except Exception as e:
        return jsonify({"status": 500})
    return jsonify({"data": json_posts, "status": 200})


@app.route("/api/edit", methods=["POST"])
def json_edit_blog():
    """
    Edit blog
    :return:
    """
    if not request.method == "POST":
        return MethodNotAllowed
    post_id = request.form.get("post_id")
    try:
        post = Post.get(Post.id==post_id)
    except Exception as e:
        return jsonify({"status": 500})
    return jsonify({"status": 200, "data": post.to_json()})


@app.route("/api/editdone", methods=["POST"])
def json_editdone_blog():
    """
    Edit blog
    :return:
    """
    if not request.method == "POST":
        return MethodNotAllowed
    post_id = request.form.get("post_id")
    print post_id
    content = request.form.get("content")
    title = request.form.get("title")
    labels = request.form.get("labels")
    try:
        post = Post.get(Post.id==int(post_id))
        post.title = title
        post.content = content
        post.save()
    except Exception as e:
        return jsonify({"status": 500})
    print post.title
    return jsonify({"status": 200, "data": post.to_json()})


@app.route("/api/remove", methods=["POST"])
def json_remove_blog():
    """
    Remove blog.
    :return:
    """
    if not request.method == "POST":
        return MethodNotAllowed
    id = request.form.get("id")
    try:
        Post.delete().where(User.id == id)
    except Exception as e:
        return jsonify({"status": 500})
    return jsonify({"status": 200})


@app.route("/api/publish", methods=["POST"])
def post_add():
    """
    Add new post to database.
    :return:
    """
    if not request.method == 'POST':
        return MethodNotAllowed
    title = request.form.get('title')
    content = request.form.get("content")
    print "%s %s" % (title, content)
    try:
        post = Post.create(title=title, content=content, user=User.get(User.id == 1))
        label_texts = request.form.get("labels", "", type=str)
        if label_texts != "":
            labels = Label.select().where(Label.text << label_texts.split("_"))
            for label in labels:
                labelRelationship = LabelRelationship()
                labelRelationship.label = label
                labelRelationship.post = post
                labelRelationship.save()
    except IntegrityError as e:
        return jsonify({"status": 500})
    except Exception as e:
        return jsonify({"status": 500})

    res = {
        "status": 200,
        "data": post.to_json()
    }
    return jsonify(res)


@app.route("/blogs/<int:id>", methods=['GET'])
def post_details(id):
    if not request.method == 'GET':
        return MethodNotAllowed
    public_post = Post.get(Post.id == id)
    return render_template("post.html", post=public_post)


def get_total_page():
    """
    Get total page num of all posts.
    :return:
    """
    count = Post.select().where(Post.status == 0).count()
    return (count / PER_PAGE_NUM + 1) \
        if count % PER_PAGE_NUM != 0 else (count / PER_PAGE_NUM)


def get_label_posts_total_page(label):
    """
    Get the page numbsers of label's relative posts.
    :return:
    """
    labelModel = Label.get(Label.text == label)
    count = (Post.select().join(LabelRelationship,
                                on=LabelRelationship.post)
             .where(LabelRelationship.label == labelModel)
             .count())
    return (count / PER_PAGE_NUM + 1) \
        if count % PER_PAGE_NUM != 0 else (count / PER_PAGE_NUM)


@app.route("/<string:text>/posts/<int:page>", methods=['GET'])
def label_relative_posts(text, page):
    """
    Get relative post with label.
    :return:
    """
    if not request.method == 'GET':
        return MethodNotAllowed

    print "test is %s " % text
    # page = request.args.get('page', 1, type=int)
    label = Label.select().where(Label.text == text).get()
    public_posts = label.get_posts(page)
    public_labels = Label.select()
    return render_template("label-index.html", posts=public_posts, labels=public_labels,
                           total=get_label_posts_total_page(text), page=page, label=label)


@app.route("/labels", methods=['GET'])
def label_index():
    """
    Get all labels
    :return:
    """
    if not request.method == 'GET':
        return MethodNotAllowed

    public_labels = (Label.select().order_by(Label.timestamp.desc()))
    return render_template("bloglist.html", public_labels)


@app.route("/label/remove", methods=['POST'])
def label_remove():
    """
    Remove label.
    :return:
    """
    if not request.method == 'POST':
        return MethodNotAllowed

    id = request.args.get('id', -1, type=int)
    if id == -1:
        raise BadRequest("No <ID> provided !")
    try:
        query = Label.delete().where(Label.id == id)
        query.execute()
    except Exception as e:
        raise InternalServerError(str(e))

    res = {"success": True}
    return res


@app.route("/remove", methods=["POST"])
def post_remove():
    """
    Post remove.
    :return:
    """
    if not request.method == "POST":
        return MethodNotAllowed

    post_id = request.args.get("id", -1, type=int)
    if post_id == -1:
        raise BadRequest('No <ID> provided!')
    try:
        query = Post.delete().where(Post.id == post_id)
        query.execute()
    except Exception as e:
        raise InternalServerError(str(e))

    res = {"success": True}
    return res


@app.route("/search", methods=['POST'])
def post_search():
    """
    Search post content by title.
    :return:
    """
    return ""


@app.route("/label/add", methods=['GET'])
def label_add():
    """
    Add new Label
    :return: label
    """
    if not request.method == "GET":
        return MethodNotAllowed

    text = request.args.get("text", "", str=type)
    if text is "":
        raise BadRequest('No <text> provided!')
    try:
        label = Label.create(text=text, user=User.get(User.id == 1))
    except Exception as e:
        raise InternalServerError(str(e))

    res = {
        "success": True,
        "data": label
    }
    return res


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
