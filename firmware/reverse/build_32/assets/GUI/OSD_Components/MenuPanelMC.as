class GUI.OSD_Components.MenuPanelMC extends GUI.OSD_Components.Gadget
{
   var BUTTON_SHUTTER_SPEED;
   var __buttonArray;
   var __buttonDescArray;
   var __buttonPosXArray;
   var __capability;
   var __menuMgr;
   var __osd;
   var _visible;
   var label;
   var shadow;
   var __panelLabel = null;
   var __panelID = null;
   var __numButtons = 0;
   var __buttonWidth = 150;
   var __buttonHeight = 40;
   var __defaultFocusItem = 0;
   static var MAX_BUTTONS = 6;
   function MenuPanelMC()
   {
      super();
      this.__menuMgr = GUI.OSD_Components.MenuManager.GetManager();
      this._visible = false;
      this.__buttonArray = new Array();
      this.__buttonDescArray = new Array();
   }
   function SetCapability(capability)
   {
      this.__capability = capability;
   }
   function IsUnlocked()
   {
      var _loc3_ = false;
      if(this.__capability != undefined && this.__capability != "")
      {
         _loc3_ = _global.VxCapability(this.__capability);
      }
      else
      {
         _loc3_ = true;
      }
      return _loc3_;
   }
   function show()
   {
      this._visible = true;
      GUI.OSD_Components.StatusLCD.GetManager().SetMenuTab(this.__panelLabel);
   }
   function hide()
   {
      this._visible = false;
   }
   function getID()
   {
      return this.__panelID;
   }
   function setLabel(label)
   {
      this.__panelLabel = label;
      this.label.text = label;
      this.shadow.text = label;
   }
   function getMovieClip()
   {
      return this;
   }
   function getOSD()
   {
      return this.__osd;
   }
   function getWidth()
   {
      return __panelWidth;
   }
   function getHeight()
   {
      return __panelHeight;
   }
   function handleCommit(name, value, wasHandled)
   {
      if(!wasHandled)
      {
         this.__osd.handleSoftKeyCommit(name,value);
      }
      this.__menuMgr.PopMenuPanel();
   }
   function addButtonDescriptor(type, id, label, optInfo)
   {
      var _loc2_ = optInfo;
      _loc2_.type = type;
      _loc2_.id = id;
      _loc2_.label = label;
      this.__buttonDescArray.push(_loc2_);
   }
   function instantiate()
   {
      var _loc5_;
      var _loc3_ = 0;
      var _loc4_;
      while(_loc3_ < this.__buttonDescArray.length)
      {
         if(this.__buttonDescArray[_loc3_].id == "Sensor_Advanced")
         {
            if(_global.gpdb.paramGetBoolean("SENSOR.REVISION_NUMBER"))
            {
               _loc4_ = this.__buttonDescArray[_loc3_];
               this.CreatePanelWidget(_loc4_);
            }
         }
         else
         {
            _loc4_ = this.__buttonDescArray[_loc3_];
            this.CreatePanelWidget(_loc4_);
         }
         _loc3_ = _loc3_ + 1;
      }
      this.PositionButtons();
   }
   function CreatePanelWidget(widgetInfo)
   {
      var _loc11_ = widgetInfo.type;
      var _loc12_ = widgetInfo.id;
      var _loc7_ = widgetInfo.label;
      var _loc8_ = widgetInfo.cbAction;
      var _loc4_ = widgetInfo.cbData;
      var _loc3_ = _loc11_ + "_" + _loc12_;
      if(this.buttonExists(_loc3_))
      {
         throw new Error("MenuPanelMC::CreatePanelWidget() Duplicate id \'" + _loc3_ + "\'");
      }
      var _loc5_;
      var _loc2_;
      var _loc13_;
      var _loc10_;
      var _loc14_;
      var _loc6_;
      var _loc0_;
      if(this.__numButtons < GUI.OSD_Components.MenuPanelMC.MAX_BUTTONS)
      {
         _loc5_ = null;
         _loc2_ = this;
         _loc13_ = null;
         _loc10_ = null;
         _loc14_ = null;
         switch(_loc11_)
         {
            case "BUTTON":
               switch(_loc8_)
               {
                  case "Goto_Panel":
                     _loc2_.attachMovie("PanelMenuButtonMC",_loc3_,_loc2_.getNextHighestDepth(),{__parent:_loc2_,__id:_loc3_,__label:_loc7_,__buttonType:"menu"});
                     break;
                  case "Parameter":
                     _loc2_.attachMovie("PanelButtonMC",_loc3_,_loc2_.getNextHighestDepth(),{__parent:_loc2_,__id:_loc3_,__label:_loc7_,__buttonType:"oneshot",__param:_loc4_});
                     break;
                  default:
                     _loc2_.attachMovie("PanelButtonMC",_loc3_,_loc2_.getNextHighestDepth(),{__parent:_loc2_,__id:_loc3_,__label:_loc7_,__buttonType:"oneshot"});
               }
               _loc5_ = _loc13_ = _loc2_[_loc3_];
               if((_loc0_ = _loc8_) === "Selector_Tab")
               {
                  _loc6_ = _loc2_[_loc4_];
                  _loc6_._visible = false;
                  _loc13_.attachTabSelector(_loc6_);
               }
               break;
            case "CHECKBOX":
               _loc2_.attachMovie("PanelCheckboxMC",_loc3_,_loc2_.getNextHighestDepth(),{__parent:_loc2_,__id:_loc3_,__label:_loc7_});
               _loc5_ = _loc10_ = _loc2_[_loc3_];
               switch(_loc8_)
               {
                  case "Parameter":
                     _loc10_.SetManagedParameter(_loc4_);
                     break;
                  case "Selector_Tab":
                     _loc6_ = _loc2_[_loc4_];
                     _loc6_._visible = false;
                     _loc10_.attachTabSelector(_loc6_);
                     if(widgetInfo.param != null)
                     {
                        _loc10_.SetManagedParameter(widgetInfo.param);
                     }
               }
               break;
            case "XBOX":
               _loc2_.attachMovie("PanelNotFlagMC",_loc3_,_loc2_.getNextHighestDepth(),{__parent:_loc2_,__id:_loc3_,__label:_loc7_});
               _loc5_ = _loc14_ = _loc2_[_loc3_];
               if((_loc0_ = _loc8_) === "Parameter")
               {
                  _loc14_.SetManagedParameter(_loc4_);
               }
         }
         this.__buttonArray.push(_loc5_);
         this.__numButtons += 1;
         _loc5_.setHandler(_loc12_,_loc8_,_loc4_,this.getOSD());
         if(_loc11_ != "XBOX")
         {
            this.AddTabTarget(_loc5_);
         }
      }
   }
   function PositionButtons()
   {
      var _loc2_;
      var _loc6_ = 0;
      var _loc3_ = 0;
      while(_loc3_ < this.__numButtons)
      {
         _loc2_ = this.__buttonArray[_loc3_];
         _loc6_ += _loc2_.getWidth();
         _loc3_ = _loc3_ + 1;
      }
      var _loc9_ = 1280;
      var _loc10_ = 50;
      var _loc5_ = 0;
      var _loc8_ = _loc6_ + _loc5_ * (this.__numButtons - 1);
      var _loc7_ = _loc9_ - _loc8_;
      if(_loc7_ < 50)
      {
         throw new Error("ERROR! MenuPanelMC::PositionButtons(): buttons (" + _loc8_ + ") exceed usable space in panel \'" + this.__panelID + "\'");
      }
      this.__buttonPosXArray = new Array();
      var _loc4_ = Math.floor(_loc7_ / 2);
      _loc3_ = 0;
      while(_loc3_ < this.__numButtons)
      {
         _loc2_ = this.__buttonArray[_loc3_];
         this.__buttonPosXArray[_loc3_] = _loc4_;
         _loc4_ += _loc2_.getWidth() + _loc5_;
         _loc3_ = _loc3_ + 1;
      }
      _loc3_ = 0;
      while(_loc3_ < this.__numButtons)
      {
         _loc2_ = this.__buttonArray[_loc3_];
         _loc2_.move(this.__buttonPosXArray[_loc3_],0);
         _loc3_ = _loc3_ + 1;
      }
   }
   function buttonExists(id)
   {
      var _loc2_ = false;
      for(var _loc3_ in this.__buttonArray)
      {
         if(id == this.__buttonArray[_loc3_].id())
         {
            _loc2_ = true;
            break;
         }
      }
      return _loc2_;
   }
   function setTabSelParam(id, paramName)
   {
      var _loc3_ = this.BUTTON_SHUTTER_SPEED;
      var _loc4_;
      if(_loc3_ == undefined)
      {
         _global.VxError("setTabSelParam Failed: btn == undefined");
      }
      else
      {
         _loc4_ = _loc3_.getTabSelector();
         if(_loc4_ == undefined)
         {
            _global.VxError("getTabSelector Failed: tabSel == undefined");
         }
         else
         {
            _loc4_.setParamChange(paramName);
         }
      }
   }
   function GetWidget(id)
   {
      var _loc2_ = this[id];
      return _loc2_;
   }
   function defaultFocusItem(focusNdx)
   {
      this.SetDefaultFocus(0,focusNdx);
   }
}
