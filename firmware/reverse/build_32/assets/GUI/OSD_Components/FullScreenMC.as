class GUI.OSD_Components.FullScreenMC extends GUI.OSD_Components.Gadget
{
   var __gpdb;
   var __progressBarMC;
   var _name;
   var _visible;
   var attachMovie;
   var getNextHighestDepth;
   var __lcdBanner = "No banner";
   function FullScreenMC()
   {
      super();
      this.__gpdb = _global.gpdb;
      this._visible = false;
      grid = new Array();
   }
   function Activate()
   {
      GUI.OSD_Components.MenuManager.GetManager().ExitMenuTree();
      GUI.OSD_Components.ScreenMgrMC.GetManager().MarkActive(this._name,true);
      GUI.OSD_Components.HudLowerMC.GetManager().Show(false);
      if(this.IsEmptyGizmoGrid())
      {
         GUI.OSD_Components.StatusLCD.GetManager().SetMessage(this.__lcdBanner);
      }
      else
      {
         GUI.OSD_Components.StatusLCD.GetManager().SetMenuTab(this.__lcdBanner);
         this.ActivateGizmoGrid();
      }
      this._visible = true;
      this.__progressBarMC.gotoAndPlay(1);
   }
   function Deactivate(restoreHUD)
   {
      _global.VxDebug("FullScreenMC::Deactivate()");
      this.__progressBarMC.gotoAndStop(1);
      this._visible = false;
      GUI.OSD_Components.ScreenMgrMC.GetManager().MarkActive(this._name,false);
      var _loc3_;
      if(restoreHUD)
      {
         while(GUI.OSD_Components.TabManager.GetManager().pop() == false)
         {
         }
         GUI.OSD_Components.HudLowerMC.GetManager().Show(true);
         _loc3_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
         if(_loc3_ == 0 || _loc3_ == 1)
         {
            this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED","true");
         }
         GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_STATUS);
      }
   }
   function SetLcdBanner(text)
   {
      this.__lcdBanner = text;
   }
   function NewProgressBar(y)
   {
      y = y !== undefined ? y : 0;
      this.__progressBarMC = this.attachMovie("CylonMC",id,this.getNextHighestDepth(),{_x:390,_y:y});
      this.__progressBarMC.gotoAndStop(1);
   }
   function NewButton(label, action, x, y, cbArg)
   {
      var _loc8_;
      var _loc4_;
      if(label === undefined || action === undefined)
      {
         _global.VxError("FullScreenMC::NewButton(" + label + ", " + action + ") Called w/ undefined arg(s).");
      }
      else
      {
         x = x !== undefined ? x : 0;
         y = y !== undefined ? y : 0;
         _loc8_ = this.NewID(label);
         _loc4_ = this.attachMovie("PanelButtonMC",_loc8_,this.getNextHighestDepth(),{__label:label,_onRelease:mx.utils.Delegate.create(this,action),__cbArgRelease:cbArg,_x:x,_y:y});
         this.AddTabTarget(GUI.OSD_Components.Gizmo(_loc4_));
         this.DistributeRow();
      }
      return GUI.OSD_Components.PanelButtonMC(_loc4_);
   }
   function NewID(name)
   {
      var _loc3_ = 0;
      var _loc2_ = "button_" + name + _loc3_.toString();
      while(this[_loc2_] != undefined)
      {
         _loc3_ += 1;
         _loc2_ = "button_" + name + _loc3_.toString();
      }
      return _loc2_;
   }
   function PositionRow(row, y)
   {
      var _loc2_ = this.CurrentRowOfGizmos();
      if(_loc2_ != undefined)
      {
         i = 0;
         while(i < _loc2_.length)
         {
            _loc2_[i]._y = y;
            i++;
         }
      }
   }
   function DistributeRow()
   {
      var _loc2_ = this.CurrentRowOfGizmos();
      var _loc5_ = _loc2_.length;
      var _loc6_ = 0;
      var _loc3_ = 0;
      var _loc7_ = 40;
      var _loc4_;
      if(_loc2_ != undefined)
      {
         i = 0;
         while(i < _loc5_)
         {
            _loc4_ = _loc2_[i];
            _loc6_ += _loc4_._width;
            i++;
         }
         _loc6_ += (_loc5_ - 1) * _loc7_;
         _loc3_ = (1280 - _loc6_) / 2;
         i = 0;
         while(i < _loc5_)
         {
            _loc2_[i]._x = _loc3_;
            _loc3_ += _loc2_[i]._width;
            _loc3_ += _loc7_;
            i++;
         }
      }
   }
}
