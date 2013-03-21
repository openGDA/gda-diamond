from polarimeter.scannable.followingErrorScannable \
                    import FollowingErrorScannable

retRotFE = FollowingErrorScannable('retRotFE', RetRotation,
                                   'ME02P-MO-RET-01:ROT')
retRotFE.configure()

anaRotFE = FollowingErrorScannable('anaRotFE', AnaRotation,
                                   'ME02P-MO-ANA-01:ROT')
anaRotFE.configure()