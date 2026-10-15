ChannelConfigHasInterface = '''<?xml version="1.0" encoding="UTF-8" ?>
    <CycloneDDS>
        <Domain Id="any">
            <General>
                <Interfaces>
                    <NetworkInterface name="$__IF_NAME__$" priority="default" multicast="default"/>
                </Interfaces>
            </General>
            <Discovery>
                <!-- default 100s: after we vanish the dog keeps ghost-reader
                     state and keeps uncasting into the dead link for the whole
                     lease -- spanning every flip recovery window. 0.5s purge
                     (announcements go to lease/3 ~ 0.17s). 2026-10-10. -->
                <LeaseDuration>500 ms</LeaseDuration>
            </Discovery>
            <Tracing>
                <Verbosity>config</Verbosity>
            <OutputFile>/tmp/cdds.LOG</OutputFile>
        </Tracing>
        </Domain>
    </CycloneDDS>'''

ChannelConfigAutoDetermine = '''<?xml version="1.0" encoding="UTF-8" ?>
    <CycloneDDS>
        <Domain Id="any">
            <General>
                <Interfaces>
                    <NetworkInterface autodetermine=\"true\" priority=\"default\" multicast=\"default\" />
                </Interfaces>
            </General>
            <Discovery>
                <LeaseDuration>500 ms</LeaseDuration>
            </Discovery>
        </Domain>
    </CycloneDDS>'''
