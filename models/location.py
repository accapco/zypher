from app import mysql
import MySQLdb

class Area:
    @staticmethod
    def get_by_region(region_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT AreaID, Area FROM Area WHERE RegionID = %s", (region_id,))
        areas = cursor.fetchall()
        cursor.close()
        return areas

class Zipcode:
    @staticmethod
    def get_by_area(area_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT ZipCodeID, ZipCode FROM Zipcode WHERE AreaID = %s", (area_id,))
        zipcodes = cursor.fetchall()
        cursor.close()
        return zipcodes

class LocationName:
    @staticmethod
    def get_region_name(region_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT RegionName FROM Region WHERE RegionID = %s", (region_id,))
        result = cursor.fetchone()
        cursor.close()  # Close the cursor
        return result

    @staticmethod
    def get_area_name(area_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT Area FROM Area WHERE AreaID = %s", (area_id,))
        result = cursor.fetchone()
        cursor.close()  # Close the cursor
        return result

    @staticmethod
    def get_zipcode(zipcode_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT ZipCode FROM Zipcode WHERE ZipCodeID = %s", (zipcode_id,))
        result = cursor.fetchone()
        cursor.close()  # Close the cursor
        return result
