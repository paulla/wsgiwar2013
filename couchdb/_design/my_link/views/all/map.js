function(doc) {
    if (doc.doc_type == "Link")
    {
	    emit(doc.userID, doc);
    }
}
