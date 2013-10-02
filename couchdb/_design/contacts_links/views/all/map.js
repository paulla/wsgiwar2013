function(doc) {
    if (doc.doc_type == "User")
    {
	doc.follower.forEach(function(follower)
			     {
				 doc.links.forEach(function(link)
						   {
						       emit([follower, doc.links[link]], {"_id": link});
						   }
						  );
			     });

    }

}
