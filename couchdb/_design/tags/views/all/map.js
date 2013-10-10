function(doc) {
    if (doc.doc_type == "Link")
    {
	if(doc.private == false)
	{
	    doc.tags.forEach(function(tag){emit(tag, 1);});
	}
 }
}
