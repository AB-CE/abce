try:
    import rpy2.robjects
    import os


    def to_r_and_csv(directory, basepath, csv=True):
        go = rpy2.robjects.r
        os.chdir(directory)
        print(__file__)
        go("source('%s/postprocess.R')" % basepath)

        all_tables = go('ls()')
        all_tables = [table for table in all_tables]
        try:
            all_tables.remove('trade_unified')
        except ValueError:
            pass
        new_tables = set()
        for table in all_tables:
            names = table.split('_')
            if len(names) > 1:
                new_tables.add(names[0])
                name = '_'.join(table.split('_')[1:])
                columns = go("names(%s)" % table)
                columns = [col for col in columns if not(col in ('round', 'id'))]
                for col in columns:
                    go("names(%s)[names(%s)=='%s'] <- '%s_%s'" %
                                (table, table, col, name, col))

        for table in new_tables:
            acquisitions = go("ls(pattern='%s_.*')" % table)
            acquisitions = [acq for acq in acquisitions]
            go("%s <- %s[c('round', 'id')]" % (table, acquisitions[0]))
            for acq in acquisitions:
                go("%s <- merge(%s, %s, by=c('round', 'id'))"
                            % (table, table, acq))
                go("rm(%s)" % acq)

        all_tables = go('ls()')
        if csv:
            for table in all_tables:
                go("write.csv2(get('%s'), file='%s.csv')" % (table, table))

        for table in new_tables:
            go("%s$round <- factor(%s$round)" % (table, table))
            go("%s$id <- factor(%s$id)" % (table, table))

        go("save(list = ls(all=TRUE), file = '%s')" % 'database.RData')
except ImportError:
    def to_r_and_csv(directory, basepath, csv=True):
        pass
