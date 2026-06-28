class GUI.OSD_Components.Clip
{
   var __firstFrame;
   var __startingMS;
   var frameCount;
   var name;
   var timecode;
   function Clip(__name, __timecode, __frameCount)
   {
      this.name = __name;
      this.timecode = __timecode;
      this.frameCount = __frameCount;
      this.__firstFrame = this.timecode.GetFramesSinceZero();
      this.__startingMS = this.timecode.GetMS();
   }
   function SetCurrentFrame(frame)
   {
      this.timecode.SetFrames(this.__firstFrame + frame);
   }
   function GetPositionMS()
   {
      return this.timecode.GetMS() - this.__startingMS;
   }
   function GetProgress()
   {
      var _loc2_;
      if(this.frameCount > 1)
      {
         _loc2_ = (this.timecode.GetFramesSinceZero() - this.__firstFrame) / (this.frameCount - 1);
         if(_loc2_ > 1)
         {
            this.timecode.SetFrames(this.__firstFrame + this.frameCount - 1);
            return 1;
         }
         if(_loc2_ < 0)
         {
            this.timecode.SetFrames(this.__firstFrame);
            return 0;
         }
         return _loc2_;
      }
      return 0;
   }
   function EndOfClip()
   {
      var _loc2_ = this.GetProgress();
      if(_loc2_ == 1)
      {
         return true;
      }
      if(_loc2_ == 0)
      {
         if(this.frameCount == 1)
         {
            return true;
         }
         return false;
      }
      return false;
   }
}
