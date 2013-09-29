function(doc) {
    if (doc.doc_type == "User")
    {
	doc.followers.forEach(function(follower){emit(follower, doc)});
    }
}
