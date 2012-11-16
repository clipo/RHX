CREATE TABLE "tblCrucible" ("i_crucibleID" INTEGER PRIMARY KEY  NOT NULL ,"i_positionNumber" INTEGER,"d_dateTime" DATETIME,"f_averageWeight" DOUBLE,"f_stdevWeight" DOUBLE,"v_notes" VARCHAR,"i_runID" INTEGER,"i_count" INTEGER,"f_averageTemp" DOUBLE,"f_averageHumidity" DOUBLE,"f_averageLight" FLOAT,"f_averagePressure" FLOAT,"f_stdevTemp" DOUBLE,"f_stdevHumidity" DOUBLE,"f_emptyWeightAverage" REAL,"f_emptyWeightStdDev" REAL,"i_emptyWeightCount" INTEGER,"f_105WeightAverage" REAL,"f_105WeightStdDev" REAL,"i_105WeightCount" INTEGER, "f_550WeightAverage" REAL, "f_550WeightStdDev" REAL, "i_550WeightCount" INTEGER, "d_emptyWeightDateTime" DATETIME, "d_105WeightDateTime" DATETIME, "d_550WeightDateTime" DATETIME);
CREATE TABLE "tblCrucibleXY" ("i_samplePosition" int PRIMARY KEY  NOT NULL , "i_xPosition" int, "i_yPosition" int, "v_type" VARCHAR(50), "f_xDistance" real, "f_yDistance" real);
CREATE TABLE "tblMeasurement" ("i_measurementID" INTEGER PRIMARY KEY  NOT NULL ,"i_sampleID" INTEGER,"i_positionNumber" INTEGER,"i_preOrPost" INTEGER,"f_weight" DOUBLE,"d_dateTime" DATETIME,"f_elapsedTimeMin" DOUBLE,"f_temperature" FLOAT,"f_pressure" FLOAT,"f_light" FLOAT,"i_runID" INTEGER,"f_standardWeight" DOUBLE,"f_elapsedTimeQuarterPower" DOUBLE,"i_count" INTEGER,"v_status" VARCHAR,"f_humidity" FLOAT,"i_repetition" INTEGER,"i_repetitionCount" INTEGER);
CREATE TABLE "tblRun" ("i_runID" INTEGER PRIMARY KEY  NOT NULL , "i_repetitions" INTEGER, "v_locationCode" VARCHAR(45),"i_numberOfSamples" INTEGER,"d_datetime" DATETIME,"v_operatorName" VARCHAR(45),"i_equilibrationDuration" INTEGER,"i_preMeasurementTimeInterval" INTEGER,"i_postMeasurementTimeInterval" INTEGER,"d_dateTimeFiring" DATETIME,"i_durationOfFiring" INTEGER,"i_temperatureOfFiring" INTEGER,"i_loggingInterval" INTEGER,"i_durationOfPreMeasurements" INTEGER,"i_numberOfPreMeasurements" INTEGER,"i_durationOfPostMeasurements" INTEGER,"i_numberOfPostMeasurements" INTEGER,"v_description" VARCHAR(255),"d_endOfFiring" DATETIME,"f_humidity" FLOAT,"f_temperature" FLOAT,"v_status" VARCHAR, "f_tempCorrection" DOUBLE, "f_rhCorrection" DOUBLE, "f_locationTemperature" REAL, "f_locationHumidity" REAL);
CREATE TABLE "tblSample" ("i_sampleID" INTEGER PRIMARY KEY  NOT NULL ,"i_positionNumber" INTEGER, "f_crucibleWeightAverage" DOUBLE,"f_crucibleWeightStdDev" DOUBLE,"f_sherdWeightInitialAverage" DOUBLE, "f_sherdWeightInitialStdDev" DOUBLE, "f_preWeightAverage" DOUBLE, "f_preWeightStdDev" DOUBLE,"f_postFireWeightAverage" DOUBLE, "f_postFireWeightStdDev" DOUBLE, "f_temperatureAverage" DOUBLE, "f_temperatureStdDev" DOUBLE,"f_humidityAverage" DOUBLE,"f_humidityStDev" DOUBLE,"f_pressureAverage" DOUBLE,"f_pressureStDev" DOUBLE,"f_lightAverage" DOUBLE,"f_lightStdDev" DOUBLE,"d_datetime" DATETIME,"i_runID" INTEGER,"i_crucibleID" INTEGER,"f_elapsedTimeMin" DOUBLE,"i_count" INTEGER,"v_description" VARCHAR(255),"v_locationCode" VARCHAR(255),"i_preOrPost" INTEGER,"i_loggingInterval" INTEGER,"v_status" VARCHAR(40),"i_preMeasurementTimeInterval" INTEGER,"f_temperature" DOUBLE,"f_humidity" DOUBLE,"i_repetitions" INTEGER, "f_locationTemperature" REAL, "f_locationHumidity" REAL, "f_preTempAverage" REAL, "f_preTempStdDev" REAL, "f_preHumidityAverage" REAL, "f_preHumidityStdDev" REAL, "f_postTempAverage" REAL,"f_postTempStdDev" REAL, "f_postHumidityAverage" REAL, "f_postHumidityStdDev" REAL );
CREATE TABLE "tblXY" ("t_lastUpdate" DATETIME DEFAULT CURRENT_TIMESTAMP, "d_lastUpdateDate" DATETIME DEFAULT CURRENT_DATE, "t_lastUpdateTime" DATETIME DEFAULT CURRENT_TIME, "i_xposition" INTEGER, "i_yposition" INTEGER check(typeof("i_yposition") = 'integer') );
CREATE UNIQUE INDEX "tblMeasurementIndex" ON "tblMeasurement" ("i_runID" ASC, "i_positionNumber" ASC, "i_measurementID" ASC, "i_sampleID" ASC, "i_preOrPost" ASC);
CREATE UNIQUE INDEX "tblRunIndex" ON "tblRun" ("i_runID" ASC, "v_locationCode" ASC, "i_numberOfSamples" ASC, "d_datetime" ASC);
CREATE UNIQUE INDEX "tblSampleIndex" ON "tblSample" ("i_sampleID" ASC, "i_positionNumber" ASC, "i_runID" ASC, "i_crucibleID" ASC, "i_preOrPost" ASC, "i_repetitions" ASC);