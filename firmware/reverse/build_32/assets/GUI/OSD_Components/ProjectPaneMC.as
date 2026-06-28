class GUI.OSD_Components.ProjectPaneMC extends MovieClip
{
   var Project_Resolution;
   var __textField;
   var burt;
   var button_cancel;
   var button_ok;
   function ProjectPaneMC()
   {
      super();
      _level0.osd.mcProjectPane.Project_Resolution.a.__textField.text = "720p";
      this.Project_Resolution.b.setLabel("1080i");
      this.button_ok.SetLabel("ok");
      this.button_cancel.SetLabel("cancel");
      this.__textField.text = "good-bye";
      this.burt.SetLabel("Radio");
      this.burt.setCheck(true);
      this.burt.gotoAndStop(4);
   }
}
