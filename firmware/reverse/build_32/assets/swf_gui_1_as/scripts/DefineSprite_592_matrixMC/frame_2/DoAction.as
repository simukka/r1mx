function RandRange(min, max)
{
   var _loc1_ = Math.floor(Math.random() * (max - min + 1)) + min;
   return _loc1_;
}
function CreateThread()
{
   if(n == 0)
   {
      var _loc5_ = "clip_" + i;
      var _loc3_ = RandRange(20,100);
      var _loc2_ = RandRange(40,180);
      var _loc6_ = RandRange(1,1270);
      var _loc4_ = 0;
      var _loc7_ = this.attachMovie("threadMC",_loc5_,this.getNextHighestDepth(),{_x:_loc6_,_y:_loc4_,_alpha:_loc3_,_xscale:_loc2_,_yscale:_loc2_});
      n = RandRange(3,3 + i);
      i++;
   }
   n -= 1;
}
if(i < numThreads)
{
   CreateThread();
}
