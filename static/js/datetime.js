function doDate()
{
    //generating the date object
    var dateobj = new Date();
    var time = dateobj.toLocaleTimeString();
    var x= time.split(":")
  	if(x[0]>=12)
    {
    	x=x[0]-12+":"+x[1]+" pm"
    }
    else if(x[0]<12)
    {
        	x=x[0]+":"+x[1]+" am"
    }
    document.getElementById("time").innerHTML = x;

}
setInterval(doDate, 100);