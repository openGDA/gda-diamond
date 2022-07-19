/*-
 * Copyright © 2022 Diamond Light Source Ltd.
 *
 * This file is part of GDA.
 *
 * GDA is free software: you can redistribute it and/or modify it under the
 * terms of the GNU General Public License version 3 as published by the Free
 * Software Foundation.
 *
 * GDA is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
 * details.
 *
 * You should have received a copy of the GNU General Public License along
 * with GDA. If not, see <http://www.gnu.org/licenses/>.
 */

package gda.scan;

import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLOutputFactory;

import com.ctc.wstx.api.WstxOutputProperties;
import com.ctc.wstx.stax.WstxInputFactory;
import com.ctc.wstx.stax.WstxOutputFactory;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.dataformat.xml.XmlFactory;
import com.fasterxml.jackson.dataformat.xml.XmlMapper;
import com.fasterxml.jackson.dataformat.xml.ser.ToXmlGenerator;
import com.fasterxml.jackson.dataformat.xml.ser.ToXmlGenerator.Feature;

public class XmlSerializationMappers {

	private XmlSerializationMappers() {
		// No constructor for utility class
	}

	/**
	 * Return new XmlMapper object that can serialize/deserialize objects to/from XML
	 * @return XmlMapper
	 */
	public static XmlMapper getXmlMapper() {
		XMLInputFactory ifactory = new WstxInputFactory();
		XMLOutputFactory ofactory = new WstxOutputFactory();
		// enable double quotes in the XML header declaration
		ofactory.setProperty(WstxOutputProperties.P_USE_DOUBLE_QUOTES_IN_XML_DECL, true);

		XmlFactory xf = XmlFactory.builder().inputFactory(ifactory).outputFactory(ofactory).build();
		XmlMapper mapper = new XmlMapper(xf);
		mapper.enable(SerializationFeature.INDENT_OUTPUT);
		mapper.enable(Feature.WRITE_XML_DECLARATION);
		mapper.setDefaultUseWrapper(false);
		return mapper;
	}

	public static class MapSerializer extends JsonSerializer<Map<String,String>> {

		public MapSerializer() {
			super();
		}

	    @Override
	    public void serialize(Map<String,String> value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
	        ToXmlGenerator xmlGen = (ToXmlGenerator) gen;
	        xmlGen.writeStartObject();
	        for (Map.Entry<String, String> entry : value.entrySet()) {

//	        	<scannableName>scannable1</scannableName>
//	        	<pv>pvForScannable1</pv>
//	        	<scannableName>scannable2</scannableName>
//	        	<pv>pv:for:scannable2</pv>

	            xmlGen.writeObjectFieldStart("scannableName");
	            xmlGen.setNextIsAttribute(false);
	            xmlGen.writeRaw(entry.getKey());
	            xmlGen.writeEndObject();

	            xmlGen.writeObjectFieldStart("pv");
	            xmlGen.setNextIsAttribute(false);
	            xmlGen.writeRaw(entry.getValue());
	            xmlGen.writeEndObject();
	        }
	        xmlGen.writeEndObject();
	    }

	}

	public static class MapDeserializer extends JsonDeserializer<Map<String,String>> {

		public MapDeserializer() {
			super();
		}

		@Override
		public Map<String, String> deserialize(JsonParser j, DeserializationContext ctxt)
				throws IOException {

			JsonNode node = j.getCodec().readTree(j);
	        var scnNameIter = node.get("scannableName").elements();
	        var pvIter = node.get("pv").elements();

	        Map<String,String> map = new LinkedHashMap<>();
	        while(scnNameIter.hasNext() && pvIter.hasNext()) {
	        	map.put(scnNameIter.next().asText(), pvIter.next().asText());
	        }
			return map;
		}

	}

	public static class ListSerializer extends JsonSerializer<List<String>> {

		public ListSerializer() {
			super();
		}

	    @Override
	    public void serialize(List<String> value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
	        ToXmlGenerator xmlGen = (ToXmlGenerator) gen;
	        xmlGen.writeStartObject();
	        for(var v : value) {
	        	xmlGen.writeObjectFieldStart(v.getClass().getSimpleName().toLowerCase());
	        	xmlGen.setNextIsAttribute(false);
	        	xmlGen.writeRaw(v.toString());
	        	xmlGen.writeEndObject();
	        }
	        xmlGen.writeEndObject();
	    }
	}

	public static class ListDeserializer extends JsonDeserializer<List<String>> {

		@Override
		public List<String> deserialize(JsonParser j, DeserializationContext ctxt)
				throws IOException {

			JsonNode node = j.getCodec().readTree(j);
			if (node == null) {
				return null;
			}

			var entry = node.fields().next();
			List<String> nestedList = new ArrayList<>();
			JsonNode value = entry.getValue();
			// Node is a single text value
			if (value.isValueNode()) {
				nestedList.add(entry.getValue().textValue());
			} else {
				// Node has 1 or more elements that can be iterated
				JsonNode nodeValues = value.elements().next();
				if (nodeValues.isValueNode()) {
					// Add single value to the list
					nestedList.add(nodeValues.textValue());
				} else {
					// Iterate over all the values and add to list
					var iterator = nodeValues.elements();
					while(iterator.hasNext()) {
						var els = iterator.next();
						nestedList.add(els.textValue());
					}
				}
			}
			return nestedList;
		}
	}

	/**
	 * {@link JsonSerializer} to convert {@code List<List<Double>>} to a
	 * 'list-of-lists' XML structure.
	 * e.g. Given : (1.0, 2.3, 4.5), (11.0, 23.0, 45.0) , XML produced is :
	 * <pre><{@code
	 * <list>
	 *  <double>1.0</double>
	 *  <double>2.3</double>
	 *  <double>4.5</double>
	 * </list>
	 * <list>
	 *   <double>11.0</double>
	 *   <double>23.0</double>
	 *   <double>45.0</double>
	 * </list>
	 *}</pre>
	 */
	public static class NestedListSerializer extends JsonSerializer<List<List<Double>>> {

		public NestedListSerializer() {
			super();
		}

	    @Override
	    public void serialize(List<List<Double>> value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
	        ToXmlGenerator xmlGen = (ToXmlGenerator) gen;
	        xmlGen.writeStartObject();
	        for (var vals : value) {
	            xmlGen.writeObjectFieldStart("list");
	        	for(Double v : vals) {
		            xmlGen.writeObjectFieldStart("double");
		            xmlGen.setNextIsAttribute(false);
		            xmlGen.writeRaw(v.toString());
		            xmlGen.writeEndObject();
	        	}
	            xmlGen.writeEndObject();
	        }
	        xmlGen.writeEndObject();
	    }
	}

	/**
	 * {@link JsonDeserializer} to convert XML produced by {@link NestedListSerializer}
	 * back to a {@code List<List<Double>>}.
	 */
	public static class NestedListDeserializer extends JsonDeserializer<List<List<Double>>> {

		@Override
		public List<List<Double>> deserialize(JsonParser j, DeserializationContext ctxt)
				throws IOException {

			JsonNode node = j.getCodec().readTree(j);
			if (node == null) {
				return null;
			}

			var dblIter = node.findValues("double");
			List<List<Double>> nestedList = new ArrayList<>();
			for(var n : dblIter) {
				// Collect doubles from iterator into a list :
				var els = n.elements();
				List<Double> valList = new ArrayList<>();
				els.forEachRemaining(v -> valList.add(v.asDouble()));
				nestedList.add(valList);
			}
			return nestedList;
		}
	}

}
