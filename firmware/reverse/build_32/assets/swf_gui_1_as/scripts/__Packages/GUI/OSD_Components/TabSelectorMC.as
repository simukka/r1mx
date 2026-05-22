class GUI.OSD_Components.TabSelectorMC extends GUI.OSD_Components.PanelWidget
{
   var __gpdb;
   var __prefix;
   var __suffix;
   var __parent;
   var __id;
   var __label;
   var __managedParamName;
   var __managedParam;
   var SELECT_LABEL;
   var __positionBar;
   var __itemsParam;
   var __jumpSize;
   var SELECT_TEXT;
   var __isDynamicList;
   var STATE_UP = "NORMAL";
   var STATE_OVER = "FOCUSED";
   var STATE_DOWN = "DOWN";
   var __autoCommit = false;
   function TabSelectorMC()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.__prefix = this.__suffix = "";
      if(this.__parent && this.__id && this.__label && this.__managedParamName)
      {
         this.__managedParam = this.__gpdb.getParam(this.__managedParamName);
         this.SELECT_LABEL.text = this.__label;
         var _loc4_ = this.attachMovie("PositionBarMC","posBar",this.getNextHighestDepth(),{_x:1083,_y:-10,__width:180});
         this.__positionBar = GUI.OSD_Components.PositionIndicatorMC(_loc4_);
         if(this.__gpdb.paramGet(this.__managedParamName) !== undefined)
         {
            this.NewStaticItemListFromParam();
         }
         this.__managedParam.options.SetAndCacheChoices();
      }
      else
      {
         _global.VxError("TabSelectorMC:CTOR() must specify parent, id, label, and managed parameter.");
      }
   }
   function setParamChange(paramName)
   {
      this.__managedParam = this.__gpdb.getParam(paramName);
      this.setContinuousUpdate(true);
   }
   function getID()
   {
      return this.__id;
   }
   function setPrefix(prefix)
   {
      if(prefix != undefined && prefix != "")
      {
         this.__prefix = prefix;
      }
   }
   function setSuffix(suffix)
   {
      if(suffix != undefined && suffix != "")
      {
         this.__suffix = suffix;
      }
   }
   function setContinuousUpdate(continuousUpdate)
   {
      this.__autoCommit = continuousUpdate;
      if(continuousUpdate)
      {
         this.__managedParam.options.AutoCommit(true);
      }
   }
   function SetParamWithItems(paramName)
   {
      if(paramName != undefined)
      {
         this.__itemsParam = paramName;
      }
   }
   function HandleParamCommit(value)
   {
      this.__gpdb.paramSet(this.__managedParamName,value);
   }
   function handleGenericCommit(value)
   {
   }
   function Reveal(visible)
   {
      this._visible = visible;
   }
   function CalculateJumpSize()
   {
      var _loc2_ = this.__managedParam.options.NumOptions();
      this.__jumpSize = Math.floor(_loc2_ / 3);
      if(this.__jumpSize < 1)
      {
         this.__jumpSize = 1;
      }
   }
   function isChanged()
   {
      return this.__managedParam.options.isChanged();
   }
   function GetValue()
   {
      return this.__gpdb.paramGet(this.__managedParamName);
   }
   function Paint()
   {
      this.SELECT_TEXT.text = this.ConstructText();
      if(this.__autoCommit)
      {
         this.__positionBar.SetMarkerIndex(this.__managedParam.options.IndexOfCurrentValue());
      }
      this.__positionBar.SetIndex(this.__managedParam.options.IndexOfSelectedValue());
      this.__positionBar.Paint();
      GUI.OSD_Components.StatusLCD.GetManager().SetSelectValue(this.SELECT_TEXT.text);
   }
   function ConstructText()
   {
      var _loc2_ = this.__managedParam.options.GetSelectionLabel();
      var _loc3_ = _loc2_ == undefined ? "None Available" : this.__prefix + _loc2_ + this.__suffix;
      if(_loc2_ == undefined)
      {
      }
      return _loc3_;
   }
   function NewDynamicItemListFromParam()
   {
      this.__isDynamicList = true;
   }
   function NewStaticItemListFromParam()
   {
      if(this.__managedParamName != null)
      {
         this.__isDynamicList = false;
      }
   }
   function StripLeadingWhiteSpace(s)
   {
      var _loc1_ = undefined;
      _loc1_ = 0;
      while(s.charAt(_loc1_) == " ")
      {
         _loc1_ = _loc1_ + 1;
      }
      if(_loc1_ == 0)
      {
         return s;
      }
      return s.substr(_loc1_);
   }
   function setLabel(label)
   {
      this.SELECT_LABEL.text = label;
   }
   function getLabel()
   {
      return this.SELECT_LABEL.text;
   }
   function press()
   {
      this.gotoAndStop(this.STATE_DOWN);
      this._onPress();
   }
   function release()
   {
      this.gotoAndStop(this.STATE_OVER);
      this._onRelease();
   }
   function releaseOutside()
   {
      this.gotoAndStop(this.STATE_UP);
      this._onReleaseOutside();
   }
   function focus()
   {
      this.rollOver();
   }
   function killFocus()
   {
      this.rollOut();
   }
   function rollOver()
   {
      this.__managedParam.options.SetAndCacheChoices();
      this.__positionBar.SetLength(this.__managedParam.options.NumOptions());
      this.__positionBar.SetMarkerIndex(this.__managedParam.options.IndexOfCurrentValue());
      this.CalculateJumpSize();
      if(this.__itemsParam != null)
      {
         this.NewDynamicItemListFromParam();
      }
      this.Paint();
      this._onRollOver();
   }
   function rollOut()
   {
      _global.osd.__sensor.hideInfo();
      this._onRollOut();
      if(!this.__isDynamicList)
      {
         this.onCommit();
      }
   }
   function onKeyDown()
   {
      if(Key.getCode() == 13)
      {
         this.press();
      }
   }
   function onKeyUp()
   {
      if(Key.getCode() == 13)
      {
         this.release();
      }
   }
   function _onPress()
   {
   }
   function _onRelease()
   {
   }
   function _onReleaseOutside()
   {
   }
   function _onFocus()
   {
   }
   function _onKillFocus()
   {
   }
   function _onRollOver()
   {
   }
   function _onRollOut()
   {
   }
   function onPress()
   {
   }
   function onRelease()
   {
   }
   function onReleaseOutside()
   {
      this.releaseOutside();
   }
   function onFocus()
   {
      this.focus();
   }
   function onKillFocus()
   {
      this.killFocus();
   }
   function onRollOver()
   {
   }
   function onRollOut()
   {
   }
   function onCommit()
   {
      if(this.__isDynamicList || this.isChanged())
      {
         this.__managedParam.options.Commit();
         _global.VxDebug("TabSelector::onCommit(" + this.__managedParamName + ") setting to \'" + this.GetValue() + "\'");
      }
      this.__positionBar.SetMarkerIndex(this.__managedParam.options.IndexOfCurrentValue());
      this.__positionBar.Paint();
   }
   function onInputEvent(name, value)
   {
      var _loc2_ = Number(value);
      switch(name)
      {
         case GUI.OSD_Components.TabManager.EVENT_UNDO:
            break;
         case GUI.OSD_Components.TabManager.EVENT_CW_JUMP:
            if(_loc2_ > 0)
            {
               this.__managedParam.options.SelectNext(this.__jumpSize);
               this.Paint();
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_CCW_JUMP:
            if(_loc2_ > 0)
            {
               this.__managedParam.options.SelectPrev(this.__jumpSize);
               this.Paint();
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_CW:
            if(_loc2_ > 0)
            {
               this.__managedParam.options.SelectNext(_loc2_);
               this.Paint();
               if(this.__managedParamName == "PAINT.WHITE_BALANCE.CURRENT")
               {
                  this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.SLAVE_MODE",0);
                  this.__gpdb.paramSet("GUI.PAINT.CW.STEP.SIZE",_loc2_);
                  this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.SLAVE_MODE",3);
               }
               if(this.__managedParamName == "PAINT.SLAVE.WHITE_BALANCE.CURRENT")
               {
                  this.__gpdb.paramSet("GUI.PAINT.CW.SLAVE.MANUAL_WHITE_BALANCE",0);
                  this.__gpdb.paramSet("GUI.PAINT.CW.SLAVE.MANUAL_WHITE_BALANCE",_loc2_);
               }
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_CCW:
            if(_loc2_ > 0)
            {
               this.__managedParam.options.SelectPrev(_loc2_);
               this.Paint();
               if(this.__managedParamName == "PAINT.WHITE_BALANCE.CURRENT")
               {
                  this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.SLAVE_MODE",0);
                  this.__gpdb.paramSet("GUI.PAINT.CCW.STEP.SIZE",_loc2_);
                  this.__gpdb.paramSet("GUI.PAINT.WHITE_BALANCE.SLAVE_MODE",4);
               }
               if(this.__managedParamName == "PAINT.SLAVE.WHITE_BALANCE.CURRENT")
               {
                  this.__gpdb.paramSet("GUI.PAINT.CCW.SLAVE.MANUAL_WHITE_BALANCE",0);
                  this.__gpdb.paramSet("GUI.PAINT.CCW.SLAVE.MANUAL_WHITE_BALANCE",_loc2_);
               }
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_SELECT:
            if(value == "false")
            {
               this.onCommit();
               this.Paint();
            }
      }
   }
}
