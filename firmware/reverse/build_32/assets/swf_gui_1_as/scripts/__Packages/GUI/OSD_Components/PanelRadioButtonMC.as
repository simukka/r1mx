class GUI.OSD_Components.PanelRadioButtonMC extends GUI.OSD_Components.PanelWidget
{
   var __textField;
   var __initialValue;
   var __linkedParam;
   var STATE_UP = "up";
   var STATE_OVER = "over";
   var STATE_DOWN = "down";
   var __checked = false;
   var __selected = false;
   var __pressed = false;
   function PanelRadioButtonMC()
   {
      super();
      this.__textField.text = "sas";
      this.setLabel("monster");
      this.__initialValue = "";
      this.update();
   }
   function setLabel(label)
   {
      this.__textField.text = label;
   }
   function getLabel()
   {
      return this.__textField.text;
   }
   function setCheck(checked)
   {
      this.__checked = checked;
      this.update();
   }
   function setSelect(selected)
   {
      this.__selected = selected;
      this.update();
   }
   function update()
   {
      var _loc2_ = undefined;
      if(this.__selected)
      {
         if(this.__checked)
         {
            this.gotoAndStop("SELECTED_CHECKED");
         }
         else
         {
            this.gotoAndStop("SELECTED_EMPTY");
         }
      }
      else if(this.__checked)
      {
         this.gotoAndStop("CHECKED");
      }
      else
      {
         this.gotoAndStop("EMPTY");
      }
   }
   function setManagedParameter(paramName)
   {
      this.__initialValue = _global.gpdb.paramGet(paramName);
      if(this.__initialValue !== undefined)
      {
         this.__linkedParam = paramName;
      }
   }
   function handleParamCommit(value)
   {
      _global.gpdb.paramSet(this.__linkedParam,value);
   }
   function press()
   {
      this.setCheck(!this.__checked);
      this._onPress();
   }
   function release()
   {
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
      this._onRollOver();
   }
   function rollOut()
   {
      this.setSelect(false);
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
   }
}
