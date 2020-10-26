    def numpy_to_file(x, file_name, **opt):
        h,w = x.shape
        src = opt.get("src", None)
        if src is not None:
            srcds = gdal.Open(src, gdal.GA_ReadOnly)
            crs   = opt.get("crs", srcds.GetProjectionRef())
            gt    = opt.get("geo_transform", srcds.GetGeoTransform())
        else:
            crs = opt.get("crs", None)
            gt  = opt.get("geo_transform", (0,1,0,0,0,-1))
        drv = gdal.GetDriverByName("GTiff")
        ds  = drv.Create(file_name, w, h, 1, gdal.GDT_Float32,
                    """COMPRESS=DEFLATE
                        ZLEVEL=4
                        BIGTIFF=IF_SAFER
                        PREDICTOR=3
                        NUM_THREADS=ALL_CPUS""".split())
        if crs:
            ds.SetProjection(crs)
        ds.SetGeoTransform(gt)
        band = ds.GetRasterBand(1)
        band.WriteArray(x)
        if opt.get("nodata", None) is not None:
            band.SetNoDataValue(opt["nodata"])
        ds.FlushCache()
