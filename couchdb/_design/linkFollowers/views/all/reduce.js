function (key, values, rereduce) {
    var tmpLinks = [];
    var users = [];
    var links = [];

    values.forEach(function(value)
		   {
		       if(value.doc_type == 'Link')
		       {
			   tmpLinks.push(value);
			   return;
		       }
		       if(value.doc_type == 'User')
		       {
			   for (follower in value.followers)
			   {
			       if (follower == 'key')
			       {
				   users.push(value._id);
				   return ;
			       }

			   };
			   return;

		       }
		   })

    tmpLinks.forEach(function(link)
		     {
			 for(user in users)
			 {
			     if(link == userID)
			     {
				 links.push(links);
				 return;
			     }

			 }
		     }
		    );

    return links
}
