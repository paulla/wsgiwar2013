function (doc)
{
    if (doc.type == 'Link'){emit(null, doc)};
    if (doc.type == 'User'){doc.followers.forEach(function(follower){emit(follower, doc);})};
}
