function CleanUp()
{
   var _loc2_ = 0;
   while(_loc2_ < 200)
   {
      var _loc3_ = this["clip_" + _loc2_];
      _loc3_.removeMovieClip();
      _loc2_ = _loc2_ + 1;
   }
}
var numThreads = 30;
var n = 5;
var i = 0;
stop();
