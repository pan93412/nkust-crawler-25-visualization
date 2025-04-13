from dataclasses import dataclass
from datetime import datetime
from typing import Literal, NotRequired, TypedDict
from bson import ObjectId


class ArticleMongoModel(TypedDict):
    _id: NotRequired[ObjectId]
    article_id: str
    url: str
    title: str
    created_at: datetime
    content: str

@dataclass
class Article:
    _id: str | None
    article_id: str
    url: str
    title: str
    created_at: datetime
    content: str

def article_from_mongo_model(mongo_model: ArticleMongoModel) -> Article:
    assert "_id" in mongo_model, "mongo_model 必須包含 _id 欄位"

    return Article(
        _id=str(mongo_model["_id"]),
        article_id=mongo_model["article_id"],
        url=mongo_model["url"],
        title=mongo_model["title"],
        created_at=mongo_model["created_at"],
        content=mongo_model["content"],
    )

class CommentMongoModel(TypedDict):
    _id: NotRequired[ObjectId]
    article_id: ObjectId
    comment_id: str  # index (article_id, comment_id)
    content: str
    created_at: datetime
    author: str
    likes: int | None
    dislikes: int | None
    reaction_type: Literal["+1", "-1", "0"] | None

@dataclass
class Comment:
    _id: str | None
    article_id: str
    comment_id: str
    content: str
    created_at: datetime
    author: str
    likes: int = 0
    dislikes: int = 0
    reaction_type: Literal["+1", "-1", "0"] = "0"

def comment_from_mongo_model(mongo_model: CommentMongoModel) -> Comment:
    assert "_id" in mongo_model, "mongo_model 必須包含 _id 欄位"

    return Comment(
        _id=str(mongo_model["_id"]),
        article_id=str(mongo_model["article_id"]),
        comment_id=mongo_model["comment_id"],
        content=mongo_model["content"],
        created_at=mongo_model["created_at"],
        author=mongo_model["author"],
        likes="likes" in mongo_model and mongo_model["likes"] or 0,
        dislikes="dislikes" in mongo_model and mongo_model["dislikes"] or 0,
        reaction_type="reaction_type" in mongo_model and mongo_model["reaction_type"] or "0",
    )

class ReplyMongoModel(TypedDict):
    _id: NotRequired[ObjectId]
    article_id: ObjectId
    comment_id: ObjectId
    reply_id: str  # index (article_id, comment_id, reply_id)
    content: str
    created_at: datetime
    author: str
    likes: int | None
    dislikes: int | None
    reaction_type: Literal["+1", "-1", "0"] | None

@dataclass
class Reply:
    _id: str | None
    article_id: str
    comment_id: str
    reply_id: str
    content: str
    created_at: datetime
    author: str
    likes: int = 0
    dislikes: int = 0
    reaction_type: Literal["+1", "-1", "0"] = "0"

def reply_from_mongo_model(mongo_model: ReplyMongoModel) -> Reply:
    assert "_id" in mongo_model, "mongo_model 必須包含 _id 欄位"

    return Reply(
        _id=str(mongo_model["_id"]),
        article_id=str(mongo_model["article_id"]),
        comment_id=str(mongo_model["comment_id"]),
        reply_id=mongo_model["reply_id"],
        content=mongo_model["content"],
        created_at=mongo_model["created_at"],
        author=mongo_model["author"],
        likes="likes" in mongo_model and mongo_model["likes"] or 0,
        dislikes="dislikes" in mongo_model and mongo_model["dislikes"] or 0,
        reaction_type="reaction_type" in mongo_model and mongo_model["reaction_type"] or "0",
    )
