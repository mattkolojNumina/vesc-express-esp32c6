function Controller() {
    installer.autoRejectMessageBoxes();
    installer.installationFinished.connect(function() {
        gui.clickButton(buttons.NextButton);
    })
}

Controller.prototype.WelcomePageCallback = function() {
    // click delay here because the next button is initially disabled for ~1 second
    gui.clickButton(buttons.NextButton, 3000);
}

Controller.prototype.CredentialsPageCallback = function() {
    gui.clickButton(buttons.SkipButton);
}

Controller.prototype.IntroductionPageCallback = function() {
    gui.clickButton(buttons.NextButton);
}

Controller.prototype.TargetDirectoryPageCallback = function() {
    gui.currentPageWidget().TargetDirectoryLineEdit.setText("/opt/Qt");
    gui.clickButton(buttons.NextButton);
}

Controller.prototype.ComponentSelectionPageCallback = function() {
    var widget = gui.currentPageWidget();

    // Deselect all first
    widget.deselectAll();

    // Select Qt 5.15.2
    widget.selectComponent("qt.qt5.5152");
    
    // Select Android components for Qt 5.15.2
    widget.selectComponent("qt.qt5.5152.android");
    widget.selectComponent("qt.qt5.5152.android_arm64_v8a");
    widget.selectComponent("qt.qt5.5152.android_x86_64");
    
    // Select Qt Creator
    widget.selectComponent("qt.tools.qtcreator");
    
    gui.clickButton(buttons.NextButton);
}

Controller.prototype.LicenseAgreementPageCallback = function() {
    gui.currentPageWidget().AcceptLicenseRadioButton.setChecked(true);
    gui.clickButton(buttons.NextButton);
}

Controller.prototype.StartMenuDirectoryPageCallback = function() {
    gui.clickButton(buttons.NextButton);
}

Controller.prototype.ReadyForInstallationPageCallback = function() {
    gui.clickButton(buttons.NextButton);
}

Controller.prototype.FinishedPageCallback = function() {
    var checkBoxForm = gui.currentPageWidget().LaunchQtCreatorCheckBoxForm;
    if (checkBoxForm && checkBoxForm.launchQtCreatorCheckBox) {
        checkBoxForm.launchQtCreatorCheckBox.checked = false;
    }
    gui.clickButton(buttons.FinishButton);
}