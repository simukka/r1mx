class GUI.OSD_Components.OsdXml extends XML
{
   var __gpdb;
   var __osd;
   var __osdMC;
   var __panelRegisterFnc;
   var firstChild;
   var onLoad;
   function OsdXml(xmlFileName, registerPanelFnc)
   {
      super();
      this.__panelRegisterFnc = registerPanelFnc;
      this.__gpdb = _global.gpdb;
      this.__osd = GUI.OSD_Components.OSD.GetManager();
      this.__osdMC = GUI.OSD_Components.OSD.getVisual();
      this.ignoreWhite = true;
      mx.events.EventDispatcher.initialize(this);
      this.onLoad = mx.utils.Delegate.create(this,this.MyOnLoad);
      this.load(xmlFileName);
   }
   function dispatchEvent()
   {
   }
   function addEventListener()
   {
   }
   function removeEventListener()
   {
   }
   function MyOnLoad(success)
   {
      var _loc3_;
      if(success)
      {
         _global.log("GuiBoot(5).......Parsing panels.xml");
         this.parseAllPanels();
         _global.log("GuiBoot(6).......Instantiating panels");
         _loc3_ = {target:this,type:"xmlPanelLoadComplete"};
         this.dispatchEvent(_loc3_);
      }
   }
   function parseAllPanels()
   {
      var _loc3_;
      var _loc2_ = this.firstChild.firstChild;
      while(_loc2_)
      {
         switch(_loc2_.nodeName)
         {
            case "Panel":
               _loc3_ = this.NewMenuPanel(_loc2_);
               break;
            case "Tab":
         }
         _loc2_ = _loc2_.nextSibling;
      }
   }
   function NewMenuPanel(aNode, forcedID)
   {
      var _loc5_ = null;
      var _loc3_;
      var _loc4_;
      var _loc0_;
      var _loc7_;
      if(aNode)
      {
         _loc3_ = aNode.attributes.type;
         if(_loc3_ == undefined)
         {
            _loc3_ = "button";
         }
         else
         {
            _loc3_ = _loc3_.toLowerCase();
         }
         _loc4_ = aNode.attributes.id;
         if(forcedID != undefined)
         {
            if(_loc4_ == undefined)
            {
               _loc4_ = forcedID;
            }
         }
         else if(_loc4_ == undefined)
         {
         }
         if((_loc0_ = _loc3_) !== "button")
         {
            _global.VxError("ERROR: OsdXml.NewMenuPanel(): Unknown panel type, assuming button");
         }
         else
         {
            _loc5_ = this.CreateMenuPanel(_loc4_,aNode);
         }
         _loc7_ = aNode.attributes.label;
         if(_loc7_ != undefined)
         {
            _loc5_.setLabel(_loc7_);
         }
         this.__panelRegisterFnc(_loc5_);
      }
      return _loc5_;
   }
   function CreateMenuPanel(panelID, aNode)
   {
      this.__osdMC.attachMovie("MenuPanelMC",panelID,this.__osdMC.getNextHighestDepth(),{_y:784,__osd:this.__osd,__panelID:panelID});
      var _loc5_ = this.__osdMC[panelID];
      var _loc8_ = 0;
      var _loc6_ = 0;
      var _loc10_ = aNode.attributes.capability;
      if(_loc10_ != undefined && _loc10_ != null)
      {
         _loc5_.SetCapability(_loc10_);
      }
      var _loc3_ = aNode.firstChild;
      var _loc4_;
      while(_loc3_ != null)
      {
         try
         {
            _loc4_;
            switch(_loc3_.nodeName)
            {
               case "Button":
                  _loc4_ = this.NewButton(_loc3_,_loc5_);
                  break;
               case "Checkbox":
                  _loc4_ = this.NewCheckbox(_loc3_,_loc5_);
                  break;
               case "NotFlag":
                  _loc4_ = this.NewNotFlag(_loc3_,_loc5_);
            }
            _loc8_;
            if("true" == _loc3_.attributes.hasFocus)
            {
               _loc8_ = _loc6_;
            }
            _loc6_ += _loc4_ == undefined ? 0 : 1;
         }
         catch(e:GUI.OSD_Components.Exception_Unimplemented)
         {
            _global.VxLog("UNIMPLEMENTED FEATURE: " + e.toString());
         }
         catch(e:Error)
         {
         }
         _loc3_ = _loc3_.nextSibling;
      }
      _loc5_.defaultFocusItem(_loc8_);
      return _loc5_;
   }
   function NewButton(node, panel)
   {
      var _loc3_;
      var _loc5_;
      var _loc11_;
      _loc3_ = new Object();
      _loc5_ = node.attributes.id;
      var _loc13_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
      var _loc12_;
      var _loc14_;
      var _loc4_;
      var _loc8_;
      var _loc9_;
      var _loc6_;
      if(_loc13_ == 0 && (_loc5_ != "STint" && _loc5_ != "SWBAL" && _loc5_ != "SFlut"))
      {
         if(_loc5_ == undefined || _loc5_ == null)
         {
            throw new Error("found an xml \'button\' with no id! " + node);
         }
         _loc12_ = node.attributes.label;
         if(_loc12_ == undefined || _loc12_ == null)
         {
            throw new Error("found an xml \'button\' with no label! " + node);
         }
         if(_loc5_ == "SHUTTER_SPEED")
         {
            if(this.__gpdb.paramGet("GUI.USER_PREF.SHUTTER_SPEED_FORMAT") == "DEGREES")
            {
               _loc12_ = "ANGLE";
            }
         }
         if("false" == node.attributes.implemented)
         {
            throw new GUI.OSD_Components.Exception_Unimplemented("Unimplemented Button: \'" + _loc5_ + ", \'" + _loc12_ + "\'");
         }
         _loc11_ = node.attributes.capability;
         if(_loc11_ != undefined && _loc11_ != null)
         {
            _loc14_ = _global.VxCapability(_loc11_);
            if(!_loc14_)
            {
               _global.VxDebug("OsdXml::NewButton(" + _loc12_ + ") lacks capability \'" + _loc11_ + "\'. Ignoring.");
               return undefined;
            }
         }
         _loc4_ = node.firstChild;
         while(_loc4_ != null)
         {
            if(_loc3_.cbAction)
            {
               throw new Error("Multiple actions requested! Using \'" + _loc3_.cbAction + "\'");
            }
            _loc3_.cbAction = _loc4_.nodeName;
            _loc3_.cbData = _loc4_.firstChild.nodeValue;
            switch(_loc3_.cbAction)
            {
               case "Goto_Panel":
               case "Gen_Event":
               case "Dispatch":
                  break;
               case "Panel":
                  _loc8_ = this.NewMenuPanel(_loc4_,"SUB_" + _loc5_);
                  _loc3_.cbAction = "Goto_Panel";
                  _loc3_.cbData = _loc8_.getID();
                  break;
               case "Parameter":
                  _loc3_.cbData = _loc4_.attributes.name;
                  _loc6_ = _global.gpdb.getParam(_loc3_.cbData);
                  if(_loc6_ == null)
                  {
                     throw new Error("Unrecognized parameter \'" + _loc3_.cbData + "\' while parsing button \'" + _loc5_ + "\'");
                  }
                  if(_loc6_.type != "boolean")
                  {
                     throw new Error("Parameter \'" + _loc3_.cbData + "\' is not a boolean");
                  }
                  break;
               case "Selector":
                  _loc9_ = this.NewSelectorTab(_loc4_,_loc5_,panel);
                  _loc3_.cbAction = "Selector_Tab";
                  _loc3_.cbData = _loc9_.getID();
                  break;
               case "LinkedTab":
                  break;
               default:
                  throw new Error("Unknown action: \'" + _loc4_.nodeName + "\'!");
            }
            _loc4_ = _loc4_.nextSibling;
         }
         panel.addButtonDescriptor("BUTTON",_loc5_,_loc12_,_loc3_);
         return _loc5_;
      }
      if(_loc13_ == 1 || _loc13_ == 2)
      {
         if(_loc5_ == undefined || _loc5_ == null)
         {
            throw new Error("found an xml \'button\' with no id! " + node);
         }
         _loc12_ = node.attributes.label;
         if(_loc12_ == undefined || _loc12_ == null)
         {
            throw new Error("found an xml \'button\' with no label! " + node);
         }
         if(_loc5_ == "SHUTTER_SPEED")
         {
            if(this.__gpdb.paramGet("GUI.USER_PREF.SHUTTER_SPEED_FORMAT") == "DEGREES")
            {
               _loc12_ = "ANGLE";
            }
         }
         if("false" == node.attributes.implemented)
         {
            throw new GUI.OSD_Components.Exception_Unimplemented("Unimplemented Button: \'" + _loc5_ + ", \'" + _loc12_ + "\'");
         }
         _loc11_ = node.attributes.capability;
         if(_loc11_ != undefined && _loc11_ != null)
         {
            _loc14_ = _global.VxCapability(_loc11_);
            if(!_loc14_)
            {
               _global.VxDebug("OsdXml::NewButton(" + _loc12_ + ") lacks capability \'" + _loc11_ + "\'. Ignoring.");
               return undefined;
            }
         }
         _loc4_ = node.firstChild;
         while(_loc4_ != null)
         {
            if(_loc3_.cbAction)
            {
               throw new Error("Multiple actions requested! Using \'" + _loc3_.cbAction + "\'");
            }
            _loc3_.cbAction = _loc4_.nodeName;
            _loc3_.cbData = _loc4_.firstChild.nodeValue;
            switch(_loc3_.cbAction)
            {
               case "Goto_Panel":
               case "Gen_Event":
               case "Dispatch":
                  break;
               case "Panel":
                  _loc8_ = this.NewMenuPanel(_loc4_,"SUB_" + _loc5_);
                  _loc3_.cbAction = "Goto_Panel";
                  _loc3_.cbData = _loc8_.getID();
                  break;
               case "Parameter":
                  _loc3_.cbData = _loc4_.attributes.name;
                  _loc6_ = _global.gpdb.getParam(_loc3_.cbData);
                  if(_loc6_ == null)
                  {
                     throw new Error("Unrecognized parameter \'" + _loc3_.cbData + "\' while parsing button \'" + _loc5_ + "\'");
                  }
                  if(_loc6_.type != "boolean")
                  {
                     throw new Error("Parameter \'" + _loc3_.cbData + "\' is not a boolean");
                  }
                  break;
               case "Selector":
                  _loc9_ = this.NewSelectorTab(_loc4_,_loc5_,panel);
                  _loc3_.cbAction = "Selector_Tab";
                  _loc3_.cbData = _loc9_.getID();
                  break;
               case "LinkedTab":
                  break;
               default:
                  throw new Error("Unknown action: \'" + _loc4_.nodeName + "\'!");
            }
            _loc4_ = _loc4_.nextSibling;
         }
         panel.addButtonDescriptor("BUTTON",_loc5_,_loc12_,_loc3_);
         return _loc5_;
      }
   }
   function NewCheckbox(node, panel)
   {
      var _loc4_;
      var _loc5_;
      _loc4_ = new Object();
      _loc5_ = node.attributes.id;
      if(_loc5_ == undefined || _loc5_ == null)
      {
         throw new Error("found an xml \'button\' with no id! " + node);
      }
      var _loc12_ = node.attributes.label;
      if(_loc12_ == undefined || _loc12_ == null)
      {
         throw new Error("found an xml \'button\' with no label! " + node);
      }
      if("false" == node.attributes.implemented)
      {
         throw new GUI.OSD_Components.Exception_Unimplemented("Unimplemented checkbox: \'" + _loc5_ + ", \'" + _loc12_ + "\'");
      }
      var _loc3_ = node.firstChild;
      var _loc8_;
      var _loc9_;
      var _loc6_;
      var _loc7_;
      while(_loc3_ != null)
      {
         _loc4_.cbAction = _loc3_.nodeName;
         _loc4_.cbData = _loc3_.firstChild.nodeValue;
         switch(_loc4_.cbAction)
         {
            case "Goto_Panel":
            case "Gen_Event":
            case "Dispatch":
               break;
            case "Parameter":
               _loc4_.cbData = _loc3_.attributes.name;
               _loc4_.param = _loc4_.cbData;
               _loc6_ = _loc3_.attributes.name;
               _loc7_ = _global.gpdb.getParam(_loc6_);
               if(_loc7_ == null)
               {
                  throw new Error("Unrecognized parameter \'" + _loc6_ + "\' while parsing checkbox \'" + _loc5_ + "\'");
               }
               if(_loc7_.type != "boolean")
               {
                  throw new Error("Checkbox widget \'" + _loc5_ + "\' found non-boolean parameter: " + _loc6_);
               }
               break;
            case "Selector":
               _loc9_ = this.NewSelectorTab(_loc3_,_loc5_,panel);
               _loc4_.cbAction = "Selector_Tab";
               _loc4_.cbData = _loc9_.getID();
               break;
            case "Panel":
               _loc8_ = this.NewMenuPanel(_loc3_,"SELECT_" + _loc5_);
               _loc4_.cbAction = "Goto_Panel";
               _loc4_.cbData = _loc8_.getID();
               break;
            default:
               throw new Error("Unknown action: \'" + _loc3_.nodeName + "\'!");
         }
         _loc3_ = _loc3_.nextSibling;
      }
      panel.addButtonDescriptor("CHECKBOX",_loc5_,_loc12_,_loc4_);
      return _loc5_;
   }
   function NewNotFlag(node, panel)
   {
      var _loc4_;
      var _loc5_;
      _loc4_ = new Object();
      _loc5_ = node.attributes.id;
      if(_loc5_ == undefined || _loc5_ == null)
      {
         throw new Error("found an xml \'button\' with no id! " + node);
      }
      var _loc12_ = node.attributes.label;
      if(_loc12_ == undefined || _loc12_ == null)
      {
         throw new Error("found an xml \'button\' with no label! " + node);
      }
      if("false" == node.attributes.implemented)
      {
         throw new GUI.OSD_Components.Exception_Unimplemented("Unimplemented xbox: \'" + _loc5_ + ", \'" + _loc12_ + "\'");
      }
      var _loc3_ = node.firstChild;
      var _loc8_;
      var _loc9_;
      var _loc6_;
      var _loc7_;
      while(_loc3_ != null)
      {
         _loc4_.cbAction = _loc3_.nodeName;
         _loc4_.cbData = _loc3_.firstChild.nodeValue;
         switch(_loc4_.cbAction)
         {
            case "Goto_Panel":
            case "Gen_Event":
            case "Dispatch":
               break;
            case "Parameter":
               _loc4_.cbData = _loc3_.attributes.name;
               _loc4_.param = _loc4_.cbData;
               _loc6_ = _loc3_.attributes.name;
               _loc7_ = _global.gpdb.getParam(_loc6_);
               if(_loc7_ == null)
               {
                  throw new Error("Unrecognized parameter \'" + _loc6_ + "\' while parsing xbox \'" + _loc5_ + "\'");
               }
               if(_loc7_.type != "boolean")
               {
                  throw new Error("NotFlag widget \'" + _loc5_ + "\' found non-boolean parameter: " + _loc6_);
               }
               break;
            case "Selector":
               _loc9_ = this.NewSelectorTab(_loc3_,_loc5_,panel);
               _loc4_.cbAction = "Selector_Tab";
               _loc4_.cbData = _loc9_.getID();
               break;
            case "Panel":
               _loc8_ = this.NewMenuPanel(_loc3_,"SELECT_" + _loc5_);
               _loc4_.cbAction = "Goto_Panel";
               _loc4_.cbData = _loc8_.getID();
               break;
            default:
               throw new Error("Unknown action: \'" + _loc3_.nodeName + "\'!");
         }
         _loc3_ = _loc3_.nextSibling;
      }
      panel.addButtonDescriptor("XBOX",_loc5_,_loc12_,_loc4_);
      return _loc5_;
   }
   function NewSelectorTab(node, parentId, parentPanel)
   {
      var _loc7_;
      var _loc5_;
      var _loc10_ = node.attributes.label;
      if(_loc10_ == undefined || _loc10_ == null)
      {
      }
      if(parentId == "SHUTTER_SPEED")
      {
         if(this.__gpdb.paramGet("GUI.USER_PREF.SHUTTER_SPEED_FORMAT") == "DEGREES")
         {
            _loc10_ = "SHUTTER ANGLE";
         }
      }
      var _loc4_;
      var _loc8_;
      var _loc3_ = node.firstChild;
      var _loc0_;
      while(_loc3_ != null)
      {
         if(_loc4_)
         {
            throw new Error("Multiple actions requested! Using \'" + _loc4_ + "\'");
         }
         _loc4_ = _loc3_.nodeName;
         if((_loc0_ = _loc4_) !== "Parameter")
         {
            throw new Error("Unrecognized action \'" + _loc3_.nodeName + "\'");
         }
         _loc5_ = _loc3_.attributes.name;
         _loc8_ = _loc5_;
         _loc3_ = _loc3_.nextSibling;
      }
      if(_loc5_ == "GUI.RECORD.SHUTTER_SPEED")
      {
         if(this.__gpdb.paramGet("GUI.USER_PREF.SHUTTER_SPEED_FORMAT") == "DEGREES")
         {
            _loc5_ = "GUI.RECORD.SHUTTER_SPEED_DEG";
         }
      }
      var _loc11_;
      var _loc9_;
      var _loc13_;
      var _loc14_;
      var _loc12_;
      if(null != _global.gpdb.getParam(_loc5_))
      {
         _loc11_ = "SELECT_TAB_" + parentId;
         _loc9_ = parentPanel.getMovieClip();
         _loc9_.attachMovie("TabSelectorMC",_loc11_,_loc9_.getNextHighestDepth(),{__parent:_loc9_,__id:_loc11_,__label:_loc10_,__managedParamName:_loc5_});
         _loc7_ = _loc9_[_loc11_];
         _loc7_.SetParamWithItems(node.attributes.ItemsParam);
         _loc13_ = node.attributes.prefix;
         if(_loc13_)
         {
            _loc7_.setPrefix(_loc13_);
         }
         _loc14_ = node.attributes.suffix;
         if(_loc14_)
         {
            _loc7_.setSuffix(_loc14_);
         }
         _loc12_ = "true" == node.attributes.continuousUpdate;
         if(_loc12_)
         {
            _loc7_.setContinuousUpdate(_loc12_);
         }
         return _loc7_;
      }
      throw new Error("Unrecognized parameter \'" + _loc5_ + "\'");
   }
}
