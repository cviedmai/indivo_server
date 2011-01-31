<?xml version='1.0' encoding='ISO-8859-1'?>
<xsl:stylesheet version = '1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform' xmlns:indivodoc="http://indivo.org/vocab/xml/documents#"
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"> 
  <xsl:output method = "xml" indent = "yes" />  
  <xsl:template match="indivodoc:Lab">
    <facts>
      <fact>
        <date_measured><xsl:value-of select='indivodoc:dateMeasured/text()' /></date_measured>
        <lab_type><xsl:value-of select='indivodoc:labType/text()' /></lab_type>
        <lab_name><xsl:value-of select='indivodoc:laboratory/indivodoc:name/text()' /></lab_name>
        <lab_address><xsl:value-of select='indivodoc:laboratory/indivodoc:address/text()' /></lab_address>
        <lab_comments><xsl:value-of select='indivodoc:comments/text()' /></lab_comments>

	<xsl:if test="indivodoc:labPanel">
	  <first_panel_name><xsl:value-of select='indivodoc:labPanel/indivodoc:name/text()' /></first_panel_name>
	</xsl:if>

	<xsl:if test="indivodoc:labTest">
	  <first_lab_test_name><xsl:value-of select='indivodoc:labTest/indivodoc:name/text()' /></first_lab_test_name>
	  <xsl:apply-templates select='indivodoc:labTest/indivodoc:result' />
	</xsl:if>
      </fact>
    </facts>
  </xsl:template>

  <xsl:template match="indivodoc:result">
    <first_lab_test_value>
    <xsl:if test="indivodoc:valueAndUnit">
      <xsl:if test="indivodoc:valueAndUnit/indivodoc:value"><xsl:value-of select="indivodoc:valueAndUnit/indivodoc:value/text()" />  <xsl:value-of select="indivodoc:valueAndUnit/indivodoc:unit/text()" /></xsl:if><xsl:if test="indivodoc:valueAndUnit/indivodoc:textValue"><xsl:value-of select="indivodoc:valueAndUnit/indivodoc:textValue/text()" /></xsl:if>
    </xsl:if>
    <xsl:if test="indivodoc:value">
      <xsl:value-of select="indivodoc:value" />
    </xsl:if>
    </first_lab_test_value>
  </xsl:template>
</xsl:stylesheet>
