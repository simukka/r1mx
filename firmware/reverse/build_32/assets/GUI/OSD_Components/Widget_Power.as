class GUI.OSD_Components.Widget_Power extends MovieClip
{
   var __POWER;
   var __gpdb;
   var __powerSource;
   var __statusBox;
   var mcBox;
   function Widget_Power()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.attachMovie("StatusBoxMC","mcBox",this.getNextHighestDepth(),{_x:18,_y:58});
      this.__statusBox = this.mcBox;
      this.setPowerSource(this.__gpdb.paramGet("SYSTEM.POWER.SOURCE"));
      this.setBattery(this.__gpdb.paramGet("SYSTEM.POWER.BATTERY.LEVEL"));
      this.addCallbacks();
   }
   function setBattery(value)
   {
      this.__POWER.text = value;
      var _loc4_;
      var _loc2_;
      var _loc3_;
      if(this.__powerSource == "battery")
      {
         _loc4_ = Number(value);
         if(_loc4_ > 25)
         {
            _loc2_ = 39168;
            this.__statusBox.SetColor("green");
         }
         else if(_loc4_ > 5)
         {
            _loc2_ = 13421568;
            this.__statusBox.SetColor("yellow");
         }
         else
         {
            _loc2_ = 16711680;
            this.__statusBox.SetColor("red");
         }
         _loc3_ = this.__POWER.getTextFormat();
         _loc3_.align = "center";
         _loc3_.color = _loc2_;
         this.__POWER.setTextFormat(_loc3_);
      }
      else
      {
         _loc3_ = this.__POWER.getTextFormat();
         _loc3_.align = "center";
         _loc3_.color = 39168;
         this.__POWER.setTextFormat(_loc3_);
         this.__statusBox.SetColor("green");
      }
   }
   function setPowerSource(value)
   {
      switch(value)
      {
         case "battery":
            this.__powerSource = "battery";
            this.gotoAndStop("FRAME_BATTERY");
            this.setBattery(this.__gpdb.paramGet("SYSTEM.POWER.BATTERY.LEVEL"));
            return;
         case "AC":
         default:
            this.__powerSource = "AC";
            this.gotoAndStop("FRAME_AC");
            return;
      }
   }
   function addCallbacks()
   {
      this.__gpdb.addCallback("SYSTEM.POWER.BATTERY.LEVEL",mx.utils.Delegate.create(this,this.update));
      this.__gpdb.addCallback("SYSTEM.POWER.SOURCE",mx.utils.Delegate.create(this,this.update));
   }
   function update(name, value)
   {
      switch(name)
      {
         case "SYSTEM.POWER.BATTERY.LEVEL":
            this.setBattery(value);
            return;
         case "SYSTEM.POWER.SOURCE":
            this.setPowerSource(value);
            return;
         default:
            return;
      }
   }
}
