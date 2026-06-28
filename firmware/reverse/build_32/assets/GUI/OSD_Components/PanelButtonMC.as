class GUI.OSD_Components.PanelButtonMC extends GUI.OSD_Components.PanelWidget
{
   var __cbArgPress;
   var __cbArgRelease;
   var __gpdb;
   var __label;
   var __param;
   var __pressed;
   var __tabSelector;
   var __textField;
   var _visible;
   var gotoAndStop;
   var STATE_UP = "up";
   var STATE_OVER = "over";
   var STATE_DOWN = "down";
   var __buttonType = "oneshot";
   function PanelButtonMC()
   {
      super();
      var _loc4_ = !this.__param ? "" : ", " + this.__param;
      this.__gpdb = _global.gpdb;
      if(this.__buttonType == "oneshot")
      {
         if(this.__param != undefined && !this.__gpdb.getParam(this.__param))
         {
            this.__param = undefined;
         }
      }
      this.__textField.text = this.__label != undefined ? this.__label : "";
      this.__pressed = false;
      this.__tabSelector = null;
   }
   function SetLabel(label)
   {
      this.__textField.text = label;
      this.__label = label;
   }
   function GetLabel()
   {
      return this.__textField.text;
   }
   function attachTabSelector(tabSelector)
   {
      this.__tabSelector = tabSelector;
      this.__buttonType = "selector";
   }
   function getTabSelector()
   {
      return this.__tabSelector;
   }
   function UpdateStatusLCD()
   {
      switch(this.__buttonType)
      {
         case "menu":
            GUI.OSD_Components.StatusLCD.GetManager().SetMenuItem(this.__label);
            return;
         case "selector":
            GUI.OSD_Components.StatusLCD.GetManager().SetSelectItem(this.__label);
            return;
         case "oneshot":
         default:
            GUI.OSD_Components.StatusLCD.GetManager().SetOneshotItem(this.__label);
            return;
      }
   }
   function press()
   {
      this.gotoAndStop(this.STATE_DOWN);
      if(this.__tabSelector != null)
      {
         this.__tabSelector.press();
      }
      else if(this.__param)
      {
         this.__gpdb.paramSet(this.__param,true);
      }
      this._onPress(this.__cbArgPress);
   }
   function release()
   {
      this.gotoAndStop(this.STATE_OVER);
      if(this.__tabSelector != null)
      {
         this.__tabSelector.release();
      }
      else if(this.__param)
      {
         this.__gpdb.paramSet(this.__param,false);
      }
      this._onRelease(this.__cbArgRelease);
   }
   function releaseOutside()
   {
      this._onReleaseOutside();
   }
   function focus()
   {
      this.rollOver();
      this.UpdateStatusLCD();
   }
   function killFocus()
   {
      this.rollOut();
   }
   function rollOver()
   {
      this.gotoAndStop(this.STATE_OVER);
      this._onRollOver();
      if(this.__tabSelector != null)
      {
         this.__tabSelector.rollOver();
         this.__tabSelector.Reveal(true);
      }
   }
   function rollOut()
   {
      this.gotoAndStop(this.STATE_UP);
      this._onRollOut();
      if(this.__tabSelector != null)
      {
         this.__tabSelector.rollOut();
         this.__tabSelector.Reveal(false);
      }
   }
   function notVisible()
   {
      this._visible = false;
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
      switch(name)
      {
         case GUI.OSD_Components.TabManager.EVENT_DOWN:
            if(value == "0")
            {
               this.release();
               this.__pressed = false;
            }
            else
            {
               this.press();
               this.__pressed = true;
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_SELECT:
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
      if(this.__tabSelector != null)
      {
         this.__tabSelector.onInputEvent(name,value);
      }
   }
}
