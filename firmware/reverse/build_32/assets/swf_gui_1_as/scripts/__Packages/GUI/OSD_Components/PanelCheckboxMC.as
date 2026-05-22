class GUI.OSD_Components.PanelCheckboxMC extends GUI.OSD_Components.PanelWidget
{
   var __gpdb;
   var __mc;
   var label;
   var __label;
   var __tabSelector;
   var __commitHandler;
   var __linkedParam;
   var STATE_UP = "up";
   var STATE_OVER = "over";
   var STATE_DOWN = "down";
   var __checked = false;
   var __selected = false;
   var __pressed = false;
   function PanelCheckboxMC()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.__mc = this;
      this.label.text = this.__label;
      this.__tabSelector = null;
      this.update();
   }
   function SetCheck(checked)
   {
      var _loc3_ = undefined;
      var _loc2_ = undefined;
      this.__checked = checked;
      _loc3_ = this.__checked.toString();
      if(this.__tabSelector != null)
      {
         if(this.__checked)
         {
            this.__tabSelector.rollOver();
            this.__tabSelector.Reveal(true);
            _loc2_ = this.__tabSelector.GetValue();
         }
         else
         {
            this.__tabSelector.rollOut();
            this.__tabSelector.Reveal(false);
         }
      }
      this.update();
      this.onCommit(_loc3_,_loc2_);
   }
   function setSelect(selected)
   {
      this.__selected = selected;
      this.update();
   }
   function SetCommitHandler(fnc)
   {
      if(fnc instanceof Function)
      {
         this.__commitHandler = fnc;
      }
      throw new Error("SetCommitHandler() requires a FUNCTION");
   }
   function attachTabSelector(tabSelector)
   {
      this.__tabSelector = tabSelector;
   }
   function update()
   {
      var _loc2_ = undefined;
      if(this.__selected)
      {
         if(this.__checked)
         {
            this.__mc.gotoAndPlay("SELECTED_CHECKED");
         }
         else
         {
            this.__mc.gotoAndPlay("SELECTED_EMPTY");
         }
         this.UpdateStatusLCD();
      }
      else if(this.__checked)
      {
         this.__mc.gotoAndPlay("CHECKED");
      }
      else
      {
         this.__mc.gotoAndPlay("EMPTY");
      }
   }
   function SetManagedParameter(paramName)
   {
      var _loc5_ = _global.gpdb.getParam(paramName);
      if(_loc5_ == null)
      {
         throw new Error("SetManagedParameter() Unknown parameter \'" + paramName + "\'");
      }
      if(_loc5_.type != "boolean")
      {
         throw new Error("SetManagedParameter() Requires BOOLEAN parameter \'" + paramName + "\'");
      }
      var _loc4_ = this.__gpdb.paramGet(paramName);
      this.__gpdb.addCallback(paramName,mx.utils.Delegate.create(this,this.HandlePdbUpdate));
      if(_loc4_ !== undefined)
      {
         this.__linkedParam = paramName;
         this.__checked = "true" == _loc4_;
         this.update();
         this.SetCommitHandler(mx.utils.Delegate.create(this,this.handleParamCommit));
      }
      throw new Error("PanelCheckboxMC::SetManagedParameter() ERROR. Unregistered parameter: \'" + paramName + "\'");
   }
   function HandlePdbUpdate(name, value)
   {
      this.__checked = "true" == value;
      this.update();
   }
   function handleParamCommit(value)
   {
      _global.gpdb.paramSet(this.__linkedParam,value);
   }
   function getDefaultTextFormat()
   {
      var _loc1_ = new TextFormat();
      _loc1_.color = 10395294;
      _loc1_.underline = false;
      _loc1_.align = "center";
      _loc1_.bold = false;
      _loc1_.font = "arial";
      _loc1_.size = 28;
      return _loc1_;
   }
   function UpdateStatusLCD()
   {
      if(this.__tabSelector != null)
      {
         if(this.__checked)
         {
            GUI.OSD_Components.StatusLCD.GetManager().SetSelectItem(this.__label);
         }
         else
         {
            GUI.OSD_Components.StatusLCD.GetManager().SetSelectItem(this.__label);
            GUI.OSD_Components.StatusLCD.GetManager().SetSelectValue("<Disabled>");
         }
      }
      else
      {
         GUI.OSD_Components.StatusLCD.GetManager().SetCheckboxItem(this.__label);
         GUI.OSD_Components.StatusLCD.GetManager().SetCheckmark(this.__checked);
      }
   }
   function onCommit(arg0, arg1)
   {
      super.onCommit(arg0,arg1);
      if(this.__commitHandler)
      {
         this.__commitHandler(this.__checked);
      }
      else
      {
         _global.VxError("ERROR! PanelCheckboxMC::onCommit() No commit handler was registered");
      }
   }
   function press()
   {
      if(this.__tabSelector != null && this.__checked)
      {
         if(this.__tabSelector.isChanged())
         {
            this.__tabSelector.press();
         }
         else
         {
            this.SetCheck(false);
         }
      }
      else
      {
         this.SetCheck(!this.__checked);
      }
      this._onPress();
   }
   function release()
   {
      if(this.__tabSelector != null && this.__checked)
      {
         this.__tabSelector.release();
      }
      this._onRelease();
   }
   function releaseOutside()
   {
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
      this.setSelect(true);
      if(this.__tabSelector != null && this.__checked)
      {
         this.__tabSelector.rollOver();
         this.__tabSelector.Reveal(true);
      }
      this._onRollOver();
   }
   function rollOut()
   {
      this.setSelect(false);
      if(this.__tabSelector != null && this.__checked)
      {
         this.__tabSelector.rollOut();
         this.__tabSelector.Reveal(false);
      }
      this._onRollOut();
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
      this.press();
   }
   function onRelease()
   {
      this.release();
   }
   function onReleaseOutside()
   {
      this.gotoAndStop(this.STATE_UP);
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
      this.rollOver();
   }
   function onRollOut()
   {
      this.rollOut();
   }
   function onKeyDown()
   {
      if(Key.getCode() == 13)
      {
         this.press();
         this.__pressed = true;
      }
   }
   function onKeyUp()
   {
      if(Key.getCode() == 13)
      {
         this.release();
         this.__pressed = false;
      }
   }
   function onInputEvent(name, value)
   {
      if(name == GUI.OSD_Components.TabManager.EVENT_SELECT)
      {
         if(value == "true")
         {
            this.press();
            this.__pressed = true;
         }
         else
         {
            this.release();
            this.__pressed = false;
         }
      }
      if(this.__tabSelector != null && this.__checked)
      {
         this.__tabSelector.onInputEvent(name,value);
      }
   }
}
