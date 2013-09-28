function(doc) {
    if (doc.doc_type == "Link")
    {
	if(doc.private == true)
	{
	    emit(doc._id, doc);
	}
 }
}
