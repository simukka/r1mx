class GUI.OSD_Components.Widget_Media extends MovieClip
{
   var __gpdb;
   var __statusBox;
   var mcBox;
   var __dmPresent;
   var __totalMb;
   var __remainingMb;
   var __secondsRemaining;
   var __MEDIA;
   var DISPLAY_AS_PERCENT = true;
   function Widget_Media()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.attachMovie("StatusBoxMC","mcBox",this.getNextHighestDepth(),{_x:18,_y:58});
      this.__statusBox = this.mcBox;
      this.__dmPresent = this.__gpdb.paramGet("MEDIA.DIGMAG.MEDIA_PATH").length > 0;
      this.__totalMb = Number(this.__gpdb.paramGet("MEDIA.DIGMAG.CAPACITY.TOTAL_MB"));
      this.__remainingMb = Number(this.__gpdb.paramGet("MEDIA.DIGMAG.CAPACITY.REMAINING_MB"));
      this.__secondsRemaining = Number(this.__gpdb.paramGet("MEDIA.DIGMAG.CAPACITY.TIME_REMAINING"));
      this.addCallbacks();
      this.paint();
      this._visible = this.__dmPresent;
   }
   function paint(value)
   {
      var _loc4_ = undefined;
      var _loc2_ = undefined;
      var _loc5_ = undefined;
      if(this.DISPLAY_AS_PERCENT)
      {
         var _loc6_ = Math.floor(100 * this.__remainingMb / this.__totalMb);
         _loc5_ = _loc6_.toString();
         if(_loc6_ > 10)
         {
            _loc2_ = "high";
         }
         else if(_loc6_ > 5)
         {
            _loc2_ = "medium";
         }
         else
         {
            _loc2_ = "low";
         }
      }
      else
      {
         var _loc7_ = Math.floor(Number(this.__secondsRemaining) / 60);
         _loc5_ = _loc7_.toString();
         if(_loc7_ > 10)
         {
            _loc2_ = "high";
         }
         else if(_loc7_ > 5)
         {
            _loc2_ = "medium";
         }
         else
         {
            _loc2_ = "low";
         }
      }
      this.__MEDIA.text = _loc5_.toString();
      switch(_loc2_)
      {
         case "high":
            _loc4_ = 39168;
            this.__statusBox.SetColor("green");
            break;
         case "medium":
            _loc4_ = 13421568;
            this.__statusBox.SetColor("yellow");
            break;
         case "low":
         default:
            _loc4_ = 16711680;
            this.__statusBox.SetColor("red");
      }
      var _loc3_ = this.__MEDIA.getTextFormat();
      _loc3_.align = "center";
      _loc3_.color = _loc4_;
      if(_loc5_.length > 2)
      {
         _loc3_.size = 24;
         this.__MEDIA._y = 22;
      }
      else
      {
         _loc3_.size = 32;
         this.__MEDIA._y = 16;
      }
      this.__MEDIA.setTextFormat(_loc3_);
   }
   function addCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.update);
      this.__gpdb.addCallback("MEDIA.DIGMAG.MEDIA_PATH",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.CAPACITY.TOTAL_MB",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.CAPACITY.REMAINING_MB",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.CAPACITY.TIME_REMAINING",_loc2_);
   }
   function update(name, value)
   {
      switch(name)
      {
         case "MEDIA.DIGMAG.MEDIA_PATH":
            this.__dmPresent = value.length > 0;
            this._visible = this.__dmPresent;
            break;
         case "MEDIA.DIGMAG.CAPACITY.TOTAL_MB":
            this.__totalMb = Number(value);
            this.paint();
            break;
         case "MEDIA.DIGMAG.CAPACITY.REMAINING_MB":
            this.__remainingMb = Number(value);
            this.paint();
            break;
         case "MEDIA.DIGMAG.CAPACITY.TIME_REMAINING":
            this.__secondsRemaining = Number(value);
            this.paint();
      }
   }
}
