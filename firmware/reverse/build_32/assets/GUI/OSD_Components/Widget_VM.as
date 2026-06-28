class GUI.OSD_Components.Widget_VM extends MovieClip
{
   var __BM;
   var __FC;
   var __LETTERdelay;
   var __SM;
   var __SPACEdelay;
   var __TICK;
   var __VM;
   var __gpdb;
   function Widget_VM(parent, xPos, yPos)
   {
      super();
      this.__gpdb = _global.gpdb;
      this.AddCallbacks();
      this.SetVM();
      this.SetFC();
      this.SetSM();
      this.__BM.text = !this.__gpdb.paramGetBoolean("GUI.ADVANCED.SENSOR_OPTION") ? "" : "*";
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("VIDEO.MONITOR.VIEW_MODE",_loc2_);
      this.__gpdb.addCallback("GUI.PAINT.TONE.APPLY_CUSTOM",_loc2_);
      this.__gpdb.addCallback("GUI.ADVANCED.SENSOR_OPTION",_loc2_);
      this.__gpdb.addCallback("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED",_loc2_);
      this.__gpdb.addCallback("GUI.MONITOR.OUTPUT_EFFECTS.MODE",_loc2_);
      this.__gpdb.addCallback("CAMERA.SLAVE_MODE_ACTIVE",_loc2_);
      this.__gpdb.addCallback("CAMERA.SLAVE_MODE_FOR_BLINKING",_loc2_);
   }
   function SetFC()
   {
      var _loc2_;
      if(this.__gpdb.paramGetBoolean("GUI.MONITOR.OUTPUT_EFFECTS.ENABLED"))
      {
         _loc2_ = this.__gpdb.paramGet("GUI.MONITOR.OUTPUT_EFFECTS.MODE");
         switch(_loc2_)
         {
            case "FALSECOLOR":
               this.__FC.text = "V";
               break;
            case "RAWCHECK":
               this.__FC.text = "E";
               break;
            case "EDGEHIGHLIGHT":
               this.__FC.text = "F";
         }
         this.__TICK.text = "√";
      }
      else
      {
         this.__FC.text = "";
         this.__TICK.text = "";
      }
   }
   function SetVM()
   {
      var _loc2_;
      var _loc3_ = this.__gpdb.paramGet("VIDEO.MONITOR.VIEW_MODE");
      var _loc4_;
      if(_loc3_ == "Raw")
      {
         _loc2_ = "RAW";
      }
      else
      {
         _loc4_ = this.__gpdb.paramGetBoolean("GUI.PAINT.TONE.APPLY_CUSTOM");
         if(_loc4_)
         {
            _loc2_ = "USR";
         }
         else
         {
            switch(_loc3_)
            {
               case "Raw":
                  _loc2_ = "RAW";
                  break;
               case "Rec 709":
                  _loc2_ = "709";
               case "REDcolor":
                  _loc2_ = "CLR";
                  break;
               case "REDspace":
               default:
                  _loc2_ = "RSP";
            }
         }
      }
      this.__VM.text = _loc2_;
   }
   function SetSM()
   {
      var _loc2_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
      var _loc3_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_FOR_BLINKING");
      if(_loc2_ == 1 || _loc2_ == 2)
      {
         switch(_loc2_)
         {
            case 1:
               this.__SM.text = "M";
               break;
            case 2:
               this.__SM.text = "S";
               break;
            case 0:
            default:
               this.__SM.text = "";
         }
      }
      else if(_loc2_ == 0)
      {
         switch(_loc3_)
         {
            case 1:
               this.__SM.text = "M";
               this.__LETTERdelay = setInterval(this,"Blinkingdelay",100);
               return;
            case 2:
               this.__SM.text = "S";
               this.__LETTERdelay = setInterval(this,"Blinkingdelay",100);
               return;
            case 0:
            default:
               this.__SM.text = "";
               this.__SPACEdelay = setInterval(this,"Blinkingdelay1",100);
               return;
         }
      }
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "GUI.PAINT.TONE.APPLY_CUSTOM":
         case "VIDEO.MONITOR.VIEW_MODE":
            this.SetVM();
            return;
         case "GUI.ADVANCED.SENSOR_OPTION":
            this.__BM.text = !this.__gpdb.paramGetBoolean("GUI.ADVANCED.SENSOR_OPTION") ? "" : "*";
            return;
         case "GUI.MONITOR.OUTPUT_EFFECTS.ENABLED":
         case "GUI.MONITOR.OUTPUT_EFFECTS.MODE":
            this.SetFC();
            return;
         case "CAMERA.SLAVE_MODE_ACTIVE":
         case "CAMERA.SLAVE_MODE_FOR_BLINKING":
            this.SetSM();
            return;
         default:
            return;
      }
   }
   function Blinkingdelay()
   {
      clearInterval(this.__LETTERdelay);
      this.__gpdb.paramSet("CAMERA.SLAVE_MODE_FOR_BLINKING",0);
   }
   function Blinkingdelay1()
   {
      clearInterval(this.__SPACEdelay);
      var _loc2_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE_BEFORE_SENDING_PARAMETERS");
      this.__gpdb.paramSet("CAMERA.SLAVE_MODE_FOR_BLINKING",_loc2_);
   }
}
