function(doc) {
    if (doc.doc_type == "User")
    {
	for(var follower in doc.followers)
	{
		for(var link in doc.links)
		{
			emit([doc.followers[follower], doc.links[link]], {"_id": link});
		}
	}
    }
}
