class GUI.OSD_Components.SetReticleWidthMC extends GUI.OSD_Components.FullScreenMC
{
   var __mc;
   var __gpdb;
   var __pdbAspect;
   var __type;
   var __pdbSize;
   var __pdbOffsetHeight;
   var __pdbOffsetWidth;
   var __reticleWidth;
   var __reticleHeight;
   var __reticleY;
   var __reticleX;
   var TITLE;
   var __operation;
   var aspectBoxMC;
   var __recordWidth = 1280;
   var __recordHeight = 720;
   var __recordX = 0;
   var __recordY = 0;
   var __WIDTH_JUMP_SIZE = 100;
   function SetReticleWidthMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR SetReticleWidthMC()");
      this.__mc = this;
      this.__gpdb = _global.gpdb;
      this._visible = false;
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.RESOLUTION",_loc2_);
   }
   function Update(name, value)
   {
      _global.VxDebug("EvfCtrlPanelMC::Update() " + name + ", " + value);
      var _loc0_ = null;
      if((_loc0_ = name) !== "PROJECT.MODE_MATRIX.RESOLUTION")
      {
         _global.VxError("SetReticleWidthMC.Update() ERROR! Unknown parameter, \'" + name + "\'. Ignoring.");
      }
      else
      {
         this.ConfigureForCurrentAspect();
         this.RenderAspectBox();
      }
   }
   function ReadReticleFromPDB()
   {
      this.__pdbAspect = this.__gpdb.paramGetNumber("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED." + this.__type + ".ASPECT");
      this.__pdbSize = this.__gpdb.paramGetNumber("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED." + this.__type + ".SIZE");
      this.__pdbOffsetHeight = this.__gpdb.paramGetNumber("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED." + this.__type + ".OFFSET.HEIGHT");
      this.__pdbOffsetWidth = this.__gpdb.paramGetNumber("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED." + this.__type + ".OFFSET.WIDTH");
      var _loc2_ = this.__gpdb.paramGet("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED." + this.__type + ".ASPECT");
      var _loc3_ = this.__gpdb.paramGet("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED." + this.__type + ".SIZE");
      var _loc5_ = this.__gpdb.paramGet("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED." + this.__type + ".OFFSET.HEIGHT");
      var _loc4_ = this.__gpdb.paramGet("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED." + this.__type + ".OFFSET.WIDTH");
      this.ConfigureForCurrentAspect();
      this.RenderAspectBox();
   }
   function SaveReticleToPDB()
   {
      var _loc3_ = this.__recordWidth - this.__reticleWidth;
      var _loc2_ = this.__recordHeight - this.__reticleHeight;
      this.__pdbAspect = this.__reticleWidth / this.__reticleHeight;
      this.__pdbSize = this.__reticleHeight / this.__recordHeight;
      this.__pdbOffsetHeight = _loc2_ != 0 ? this.__reticleY / _loc2_ : 0.5;
      this.__pdbOffsetWidth = _loc3_ != 0 ? this.__reticleX / _loc3_ : 0.5;
      this.__gpdb.paramSet("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED." + this.__type + ".ASPECT",this.__pdbAspect);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED." + this.__type + ".SIZE",this.__pdbSize);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED." + this.__type + ".OFFSET.HEIGHT",this.__pdbOffsetHeight);
      this.__gpdb.paramSet("GUI.OSD.RETICLE.TV_SAFE_AREA.USER_DEFINED." + this.__type + ".OFFSET.WIDTH",this.__pdbOffsetWidth);
   }
   function Activate(type)
   {
      super.Activate();
      this.__type = type;
      switch(this.__type)
      {
         case "ACTION":
            this.TITLE.text = "User-defined Safe-Action Reticle";
            break;
         case "TITLE":
            this.TITLE.text = "User-defined Safe-Title Reticle";
      }
      this.ReadReticleFromPDB();
      this.RenderAspectBox();
      this.__operation = "SET_WIDTH";
      this.gotoAndStop(this.__operation);
      this._visible = true;
   }
   function ConfigureForCurrentAspect()
   {
      var _loc2_ = undefined;
      switch(this.__gpdb.paramGet("PROJECT.MODE_MATRIX.RESOLUTION"))
      {
         case "4K2:1":
         case "3K2:1":
         case "2K2:1":
            _loc2_ = "2:1";
            break;
         case "4K1.2:1":
         case "3K1.2:1":
         case "2K1.2:1":
         case "4K40":
            _loc2_ = "1.2:1";
            break;
         case "4KHD":
         case "4KOS":
         case "RGB1080P":
         case "4KHS":
         case "4K":
         case "3K":
         case "2K":
         default:
            _loc2_ = "16:9";
      }
      switch(_loc2_)
      {
         case "1.2:1":
            this.__recordWidth = 1280;
            this.__recordHeight = 534;
            this.__recordX = 0;
            this.__recordY = 93;
            this.__mc.BACKGROUND.gotoAndStop(2);
            break;
         case "2:1":
            this.__recordWidth = 1280;
            this.__recordHeight = 640;
            this.__recordX = 0;
            this.__recordY = 40;
            this.__mc.BACKGROUND.gotoAndStop(3);
            break;
         case "16:9":
         default:
            this.__recordWidth = 1280;
            this.__recordHeight = 720;
            this.__recordX = 0;
            this.__recordY = 0;
            this.__mc.BACKGROUND.gotoAndStop(1);
      }
      this.__reticleHeight = Math.round(this.__pdbSize * this.__recordHeight / 2) * 2;
      if(this.__reticleHeight > this.__recordHeight)
      {
         this.__reticleHeight = this.__recordHeight;
      }
      this.__reticleWidth = Math.round(this.__reticleHeight * this.__pdbAspect / 2) * 2;
      if(this.__reticleWidth > this.__recordWidth)
      {
         this.__reticleWidth = this.__recordWidth;
      }
      this.__reticleX = Math.round((this.__recordWidth - this.__reticleWidth) * this.__pdbOffsetWidth);
      this.__reticleY = Math.round((this.__recordHeight - this.__reticleHeight) * this.__pdbOffsetHeight);
   }
   function ModifyWidth(pixDelta)
   {
      this.__reticleWidth += 2 * pixDelta;
      if(this.__reticleWidth < 400)
      {
         this.__reticleWidth = 400;
      }
      else if(this.__reticleWidth > this.__recordWidth)
      {
         this.__reticleWidth = this.__recordWidth;
      }
      this.__reticleX = Math.round((this.__recordWidth - this.__reticleWidth) * this.__pdbOffsetWidth);
      this.RenderAspectBox();
   }
   function ModifyHeight(pixDelta)
   {
      this.__reticleHeight += 2 * pixDelta;
      if(this.__reticleHeight < 300)
      {
         this.__reticleHeight = 300;
      }
      else if(this.__reticleHeight > this.__recordHeight)
      {
         this.__reticleHeight = this.__recordHeight;
      }
      this.__reticleY = Math.round((this.__recordHeight - this.__reticleHeight) * this.__pdbOffsetHeight);
      this.RenderAspectBox();
   }
   function ModifyX(pixDelta)
   {
      var _loc2_ = this.__recordWidth - this.__reticleWidth;
      this.__reticleX += pixDelta;
      if(this.__reticleX < 0)
      {
         this.__reticleX = 0;
      }
      else if(this.__reticleX > _loc2_)
      {
         this.__reticleX = _loc2_;
      }
      this.RenderAspectBox();
   }
   function ModifyY(pixDelta)
   {
      var _loc2_ = this.__recordHeight - this.__reticleHeight;
      this.__reticleY += pixDelta;
      if(this.__reticleY < 0)
      {
         this.__reticleY = 0;
      }
      else if(this.__reticleY > _loc2_)
      {
         this.__reticleY = _loc2_;
      }
      this.RenderAspectBox();
   }
   function RenderAspectBox()
   {
      this.aspectBoxMC.Configure(this.__reticleWidth,this.__reticleHeight,this.__reticleX + this.__recordX,this.__reticleY + this.__recordY);
   }
   function AdjustReticle(pixDelta)
   {
      switch(this.__operation)
      {
         case "SET_WIDTH":
            this.ModifyWidth(pixDelta);
            break;
         case "SET_HEIGHT":
            this.ModifyHeight(pixDelta);
            break;
         case "SET_X":
            this.ModifyX(pixDelta);
            break;
         case "SET_Y":
            this.ModifyY(pixDelta);
            break;
         case "RESET":
      }
   }
   function NextOp()
   {
      switch(this.__operation)
      {
         case "SET_WIDTH":
            this.__operation = "SET_HEIGHT";
            this.__lcdBanner = "Set Reticle Height";
            break;
         case "SET_HEIGHT":
            this.__operation = "SET_X";
            this.__lcdBanner = "Set Reticle X";
            break;
         case "SET_X":
            this.__operation = "SET_Y";
            this.__lcdBanner = "Set Reticle Y";
            break;
         case "SET_Y":
            this.__operation = "RESET";
            this.__lcdBanner = "Reset Reticle";
            break;
         case "RESET":
            this.__operation = "RESET";
            this.__lcdBanner = "Reset Reticle";
      }
      this.gotoAndStop(this.__operation);
      GUI.OSD_Components.StatusLCD.GetManager().SetMessage(this.__lcdBanner);
   }
   function PrevOp()
   {
      switch(this.__operation)
      {
         case "SET_WIDTH":
            this.__operation = "SET_WIDTH";
            this.__lcdBanner = "Set Reticle Width";
            break;
         case "SET_HEIGHT":
            this.__operation = "SET_WIDTH";
            this.__lcdBanner = "Set Reticle Width";
            break;
         case "SET_X":
            this.__operation = "SET_HEIGHT";
            this.__lcdBanner = "Set Reticle Height";
            break;
         case "SET_Y":
            this.__operation = "SET_X";
            this.__lcdBanner = "Set Reticle X";
            break;
         case "RESET":
            this.__operation = "SET_Y";
            this.__lcdBanner = "Set Reticle Y";
      }
      this.gotoAndStop(this.__operation);
      GUI.OSD_Components.StatusLCD.GetManager().SetMessage(this.__lcdBanner);
   }
   function onInputEvent(name, value)
   {
      var _loc4_ = value == "true";
      switch(name)
      {
         case GUI.OSD_Components.TabManager.EVENT_RIGHT:
            if(value == "1")
            {
               this.NextOp();
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_LEFT:
            if(value == "1")
            {
               this.PrevOp();
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_EXIT:
         case GUI.OSD_Components.TabManager.EVENT_UP:
            if(_loc4_ || value == "1")
            {
               super.Deactivate(true);
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_SELECT:
         case GUI.OSD_Components.TabManager.EVENT_DOWN:
            if((_loc4_ || value == "1") && this.__operation == "RESET")
            {
               this.SaveReticleToPDB();
               super.Deactivate(true);
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_CW:
            this.AdjustReticle(Number(value));
            break;
         case GUI.OSD_Components.TabManager.EVENT_CCW:
            this.AdjustReticle(- Number(value));
            break;
         case GUI.OSD_Components.TabManager.EVENT_CW_JUMP:
            this.AdjustReticle(this.__WIDTH_JUMP_SIZE);
            break;
         case GUI.OSD_Components.TabManager.EVENT_CCW_JUMP:
            this.AdjustReticle(- this.__WIDTH_JUMP_SIZE);
      }
   }
}
