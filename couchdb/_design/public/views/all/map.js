function(doc) {
    if (doc.doc_type == "Link")
    {
	if(doc.private == false)
	{
	    emit(doc.created, doc);
	}
 }
}
